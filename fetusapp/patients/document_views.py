from io import BytesIO

from flask import Blueprint, Response, abort, jsonify, request, send_file
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import PatientDocument
from fetusapp.storage_client import (
    delete_blob,
    download_blob,
    ensure_patient_folder,
    upload_blob,
)

documents = Blueprint("documents", __name__)


# Allowed file extensions and their MIME types
ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
}

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_content_type(filename: str) -> str:
    """Get the content type for a file based on its extension."""
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return ALLOWED_EXTENSIONS.get(ext, "application/octet-stream")


@documents.post("/documents/upload/<int:patient_id>")
@login_required
@csrf.exempt  # We'll handle CSRF in the frontend
def upload_documents(patient_id: int) -> Response:
    """
    Upload one or multiple documents for a patient.
    """
    # Verify patient exists
    from fetusapp.models import Patient

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"success": False, "error": "Patient not found"}), 404

    # Authorization check: Verify user has access to this patient
    # For now, all authenticated users can upload (adjust based on your access control)
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    # Check if files were provided
    if "files[]" not in request.files:
        return jsonify({"success": False, "error": "No files provided"}), 400

    files = request.files.getlist("files[]")

    if not files or all(f.filename == "" for f in files):
        return jsonify({"success": False, "error": "No files selected"}), 400

    uploaded_files = []
    errors = []

    # Get the folder path for this patient
    folder_path = ensure_patient_folder(patient_id)

    for file in files:
        if file.filename == "":
            continue

        filename = file.filename

        # Validate file extension
        if not allowed_file(filename):
            errors.append(
                {
                    "filename": filename,
                    "error": "File type not allowed. Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG",
                }
            )
            continue

        # Read file data
        file_data = file.read()

        # Validate file size
        if len(file_data) > MAX_FILE_SIZE:
            errors.append(
                {
                    "filename": filename,
                    "error": "File size exceeds maximum allowed size of 10MB",
                }
            )
            continue

        # Construct blob path
        blob_path = f"{folder_path}/{filename}"
        content_type = get_content_type(filename)

        try:
            # Upload to Azure Blob Storage (will check for duplicates)
            blob_url, file_size = upload_blob(
                file_data=file_data,
                blob_path=blob_path,
                content_type=content_type,
                check_duplicate=True,
            )

            # Create database record
            doc = PatientDocument(
                patient_id=patient_id,
                original_filename=filename,
                blob_path=blob_path,
                content_type=content_type,
                size_bytes=file_size,
                created_by=current_user.id,
            )
            db.session.add(doc)
            db.session.commit()

            uploaded_files.append(
                {
                    "id": doc.id,
                    "filename": filename,
                    "size": file_size,
                    "created_on": doc.created_on.isoformat()
                    if doc.created_on
                    else None,
                }
            )

        except FileExistsError as e:
            errors.append({"filename": filename, "error": str(e)})
        except Exception as e:
            errors.append({"filename": filename, "error": f"Upload failed: {str(e)}"})
            # Rollback this specific transaction
            db.session.rollback()

    # Return results
    response_data = {
        "success": len(uploaded_files) > 0,
        "uploaded": uploaded_files,
        "errors": errors,
        "summary": {
            "total": len(files),
            "successful": len(uploaded_files),
            "failed": len(errors),
        },
    }

    status_code = 200 if len(uploaded_files) > 0 else 400
    return jsonify(response_data), status_code


@documents.get("/documents/<int:doc_id>")
@login_required
@csrf.exempt
def view_document(doc_id: int) -> Response:
    """
    View/download a document from Azure Blob Storage.
    """
    # Get the document record from database
    doc = PatientDocument.query.get(doc_id)

    if not doc:
        abort(404, description="Document not found")

    # Check if document is deleted
    if doc.status == "deleted":
        abort(404, description="Document has been deleted")

    # Verify patient exists (ensures document belongs to a valid patient)
    from fetusapp.models import Patient

    patient = Patient.query.get(doc.patient_id)
    if not patient:
        abort(404, description="Associated patient not found")

    # Authorization check: Verify user has access to this patient's documents
    # For now, all authenticated users can access (adjust based on your access control)
    if not current_user.is_authenticated:
        abort(401, description="Authentication required")

    try:
        # Download the blob from Azure Storage
        content, content_type = download_blob(doc.blob_path)

        # Create a BytesIO object from the content
        file_stream = BytesIO(content)

        # Send the file to the browser
        return send_file(
            file_stream,
            mimetype=content_type,
            as_attachment=False,  # Display in browser if possible
            download_name=doc.original_filename,
        )

    except Exception as e:
        # Log the error in production
        print(f"Error retrieving document {doc_id}: {str(e)}")
        abort(500, description="Error retrieving document")


@documents.delete("/documents/<int:doc_id>")
@login_required
@csrf.exempt
def delete_document(doc_id: int) -> Response:
    """
    Delete a document (soft delete by default, with option for hard delete).
    """
    # Get the document record from database
    doc = PatientDocument.query.get(doc_id)

    if not doc:
        return jsonify({"success": False, "error": "Document not found"}), 404

    # Check if already deleted
    if doc.status == "deleted":
        return jsonify({"success": False, "error": "Document already deleted"}), 400

    # Verify patient exists (ensures document belongs to a valid patient)
    from fetusapp.models import Patient

    patient = Patient.query.get(doc.patient_id)
    if not patient:
        return jsonify({"success": False, "error": "Associated patient not found"}), 404

    # Authorization check: Verify user has access to this patient's documents
    # For now, all authenticated users can delete (adjust based on your access control)
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    # Check if physical delete is requested (query param)
    physical_delete = request.args.get("physical", "false").lower() == "true"

    try:
        if physical_delete:
            # Hard delete: Remove from Azure and database
            try:
                delete_blob(doc.blob_path)
            except Exception as e:
                # Log but don't fail if blob doesn't exist
                print(f"Warning: Could not delete blob {doc.blob_path}: {str(e)}")

            # Delete from database
            db.session.delete(doc)
            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Document permanently deleted",
                        "doc_id": doc_id,
                    }
                ),
                200,
            )

        else:
            # Soft delete: Mark as deleted in database AND remove from Azure
            # This allows the same filename to be uploaded again
            try:
                delete_blob(doc.blob_path)
            except Exception as e:
                # Log but don't fail if blob doesn't exist
                print(f"Warning: Could not delete blob {doc.blob_path}: {str(e)}")

            doc.status = "deleted"
            doc.deleted_at = db.func.now()
            doc.deleted_by = current_user.id

            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Document marked as deleted",
                        "doc_id": doc_id,
                    }
                ),
                200,
            )

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting document {doc_id}: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Failed to delete document: {str(e)}"}
            ),
            500,
        )
