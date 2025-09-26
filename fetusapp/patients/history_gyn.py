from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import GynHistory

from .forms import GynHistoryEntryForm

gyn_history = Blueprint("gyn_history", __name__)


@gyn_history.route("/api/gyn-history/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_gyn_history(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = GynHistory.query.get_or_404(id)

        # Read and normalize JSON payload so WTForms validators accept booleans
        payload = request.get_json(silent=True) or {}

        form = GynHistoryEntryForm(data=payload)

        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        value = form._fields[field].data
                        if value != "" and value is not None:
                            setattr(history, field, value)
                        else:
                            setattr(history, field, None)

            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()
            # print("-----------------------------------------------------------------"*12)
            # print(f"Updated pregnancy history: {history.to_dict()}")

            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@gyn_history.route("/api/gyn-history", methods=["POST"])
@login_required
@csrf.exempt
def create_gyn_history() -> tuple[dict, int]:
    try:
        payload = request.get_json(silent=True) or {}
        patient_id = payload.get("patient_id")
        print("Patient ID:", patient_id)
        if not patient_id:
            return jsonify({"success": False, "error": "Missing patient_id"}), 400

        form = GynHistoryEntryForm(data=payload)

        # Remove 'id' from payload for creation (let DB handle it)
        if "id" in payload:
            del payload["id"]

        # Set required system fields
        payload["patient_id"] = patient_id
        payload["created_by"] = current_user.id
        payload["last_updated_by"] = current_user.id

        if form.validate():
            new_history = GynHistory(
                patient_id=patient_id,
                created_by=current_user.id,
                last_updated_by=current_user.id,
                date_of_visit=form.date_of_visit.data,
            )

            for field in form._fields:
                if field not in [
                    "csrf_token",
                    "submit",
                    "patient_id",
                    "created_by",
                    "last_updated_by",
                ]:
                    if field in payload:
                        setattr(new_history, field, form._fields[field].data)

            new_history.created_by = current_user.id
            new_history.created_on = datetime.utcnow()
            new_history.last_updated_by = current_user.id
            new_history.last_updated_on = datetime.utcnow()

            print("Creating new gynaecological history:", new_history.to_dict())

            db.session.add(new_history)
            db.session.commit()
            return jsonify({"success": True, "id": new_history.id}), 201
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@gyn_history.route("/api/gyn_history/<int:id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_gyn_history(id: int) -> tuple[dict, int]:
    try:
        history = GynHistory.query.get_or_404(id)
        if not history:
            return (
                jsonify(
                    {"success": False, "error": "Gynaecological history not found"}
                ),
                404,
            )
        # Soft delete: mark as inactive and update metadata
        history.is_active = False
        history.last_updated_by = current_user.id
        history.last_updated_on = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
