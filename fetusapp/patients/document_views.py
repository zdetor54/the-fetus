from io import BytesIO

from flask import Blueprint, Response, abort, send_file
from flask_login import login_required

from fetusapp import csrf  # type: ignore[has-type]
from fetusapp.models import PatientDocument
from fetusapp.storage_client import download_blob

documents = Blueprint("documents", __name__)

gyn_history = Blueprint("gyn_history", __name__)


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

    # TODO: Add authorization check to ensure user has access to this patient's documents
    # For now, assuming all logged-in users can access

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


# @documents.get("/patient/<pid>/_ping")
# @login_required
# @csrf.exempt
# def docs_ping(pid: str) -> tuple[dict, int] | dict:
#     try:
#         patient = Patient.query.get(pid)
#         if not patient:
#             return {"ok": False, "error": "patient not found"}, 404

#         docs = (
#             PatientDocument.query.filter_by(patient_id=pid)
#             .filter(PatientDocument.status != "deleted")
#             .order_by(PatientDocument.created_on.desc())
#             .all()
#         )

#         return {"ok": True, "count": len(docs)}
#     except Exception as e:
#         return {"ok": False, "error": str(e)}, 500
