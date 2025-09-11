from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import HistoryObstetrics, HistoryObstetrics_x

from .forms import HistoryObstetricsForm, HistoryObstetricsXEntryForm

obstetrics_history = Blueprint("obstetrics_history", __name__)
obstetrics_history_x = Blueprint("obstetrics_history_x", __name__)


@obstetrics_history.route("/api/obstetrics-history/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_obstetrics_history(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = HistoryObstetrics.query.get_or_404(id)

        # Read and normalize JSON payload so WTForms validators accept booleans
        payload = request.get_json(silent=True) or {}

        form = HistoryObstetricsForm(data=payload)

        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        setattr(history, field, form._fields[field].data)

            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()

            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@obstetrics_history.route("/api/obstetrics-history", methods=["POST"])
@login_required
@csrf.exempt
def create_obstetrics_history() -> tuple[dict, int]:
    try:
        payload = request.get_json(silent=True) or {}
        patient_id = payload.get("patient_id")
        print("Patient ID:", patient_id)
        if not patient_id:
            return jsonify({"success": False, "error": "Missing patient_id"}), 400

        form = HistoryObstetricsForm(data=payload)

        # Remove 'id' from payload for creation (let DB handle it)
        if "id" in payload:
            del payload["id"]

        # Set required system fields
        payload["patient_id"] = patient_id
        payload["created_by"] = current_user.id
        payload["last_updated_by"] = current_user.id

        if form.validate():
            new_history = HistoryObstetrics(
                patient_id=patient_id,
                created_by=current_user.id,
                last_updated_by=current_user.id,
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

            db.session.add(new_history)
            db.session.commit()
            return jsonify({"success": True, "id": new_history.id}), 201
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@obstetrics_history.route("/api/obstetrics-history/<int:id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_obstetrics_history(id: int) -> tuple[dict, int]:
    try:
        history = HistoryObstetrics.query.get_or_404(id)
        if not history:
            return (
                jsonify({"success": False, "error": "Medical history not found"}),
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


@obstetrics_history_x.route("/api/obstetrics-history-x/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_obstetrics_history_x(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = HistoryObstetrics_x.query.get_or_404(id)
        print("Updating HistoryObstetrics_x ID:", id)
        print("Existing Data:", history.__dict__)

        # Read and normalize JSON payload so WTForms validators accept booleans
        payload = request.get_json(silent=True) or {}

        form = HistoryObstetricsXEntryForm(data=payload)

        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        setattr(history, field, form._fields[field].data)

            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()

            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@obstetrics_history_x.route("/api/obstetrics-history-x", methods=["POST"])
@login_required
@csrf.exempt
def create_obstetrics_history_x() -> tuple[dict, int]:
    try:
        payload = request.get_json(silent=True) or {}
        patient_id = payload.get("patient_id")
        print("Patient ID:", patient_id)
        if not patient_id:
            return jsonify({"success": False, "error": "Missing patient_id"}), 400

        form = HistoryObstetricsXEntryForm(data=payload)

        # Remove 'id' from payload for creation (let DB handle it)
        if "id" in payload:
            del payload["id"]

        # Set required system fields
        payload["patient_id"] = patient_id
        payload["created_by"] = current_user.id
        payload["last_updated_by"] = current_user.id

        if form.validate():
            new_history = HistoryObstetrics_x(
                patient_id=patient_id,
                created_by=current_user.id,
                last_updated_by=current_user.id,
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

            db.session.add(new_history)
            db.session.commit()
            return jsonify({"success": True, "id": new_history.id}), 201
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@obstetrics_history_x.route("/api/obstetrics-history-x/<int:id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_obstetrics_history_x(id: int) -> tuple[dict, int]:
    try:
        history = HistoryObstetrics_x.query.get_or_404(id)
        if not history:
            return (
                jsonify({"success": False, "error": "Medical history not found"}),
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
