from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import HistoryMedical

from .forms import HistoryMedicalForm

medical_history = Blueprint("medical_history", __name__)


def calculate_bmi(weight: float | None, height: float | None) -> float | str:
    try:
        if weight and height:
            return round(float(weight) / (float(height) ** 2), 2)
    except Exception:
        pass
    return ""


@medical_history.route("/api/medical-history/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_medical_history(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = HistoryMedical.query.get_or_404(id)

        # Read and normalize JSON payload so WTForms validators accept booleans
        payload = request.get_json(silent=True) or {}

        # Calculate BMI and add to payload if weight and height are present
        payload["bmi"] = calculate_bmi(
            weight=payload.get("weight"), height=payload.get("height")
        )

        # Only convert for BooleanFields and clean text fields
        form_for_types = HistoryMedicalForm()
        for field_name, field in form_for_types._fields.items():
            if field.type == "BooleanField" and field_name in payload:
                if payload[field_name] == "True":
                    payload[field_name] = True
                elif payload[field_name] == "False":
                    payload[field_name] = False
            if field.type in ["StringField", "TextAreaField"]:
                val = payload.get(field_name, "")
                val = val.strip() if isinstance(val, str) else val
                payload[field_name] = val if val else None

        form = HistoryMedicalForm(data=payload)

        if form.validate():
            # Update history fields from form data

            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        value = form._fields[field].data
                        if value == "" and form._fields[field].type in [
                            "StringField",
                            "TextAreaField",
                        ]:
                            setattr(history, field, None)
                        else:
                            setattr(history, field, value)

            # Update metadata
            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()

            # preserve the original created_by and created_on fields as well as the patient_id

            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "errors": form.errors}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@medical_history.route("/api/medical-history", methods=["POST"])
@login_required
@csrf.exempt
def create_medical_history() -> tuple[dict, int]:
    try:
        payload = request.get_json(silent=True) or {}
        patient_id = payload.get("patient_id")
        print("Patient ID:", patient_id)
        if not patient_id:
            return jsonify({"success": False, "error": "Missing patient_id"}), 400

        # Calculate BMI if weight and height are present
        payload["bmi"] = calculate_bmi(
            weight=payload.get("weight"), height=payload.get("height")
        )

        # Normalize booleans and clean text fields
        form_for_types = HistoryMedicalForm()
        for field_name, field in form_for_types._fields.items():
            if field.type == "BooleanField" and field_name in payload:
                if payload[field_name] == "True":
                    payload[field_name] = True
                elif payload[field_name] == "False":
                    payload[field_name] = False
            if field.type in ["StringField", "TextAreaField"]:
                val = payload.get(field_name, "")
                val = val.strip() if isinstance(val, str) else val
                payload[field_name] = val if val else None

        # Remove 'id' from payload for creation (let DB handle it)
        if "id" in payload:
            del payload["id"]

        # Set required system fields
        payload["patient_id"] = patient_id
        payload["created_by"] = current_user.id
        payload["last_updated_by"] = current_user.id

        form = HistoryMedicalForm(data=payload)

        if form.validate():
            # Create instance with required fields
            history = HistoryMedical(
                patient_id=patient_id,
                created_by=current_user.id,
                last_updated_by=current_user.id,
            )
            # Set all other fields dynamically, like in PUT
            for field in form._fields:
                if field not in [
                    "csrf_token",
                    "submit",
                    "patient_id",
                    "created_by",
                    "last_updated_by",
                ]:
                    if field in payload:
                        value = form._fields[field].data
                        if value == "" and form._fields[field].type in [
                            "StringField",
                            "TextAreaField",
                        ]:
                            setattr(history, field, None)
                        else:
                            setattr(history, field, value)
            db.session.add(history)
            db.session.commit()
            return jsonify({"success": True, "id": history.id}), 201
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@medical_history.route("/api/medical-history/<int:id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_medical_history(id: int) -> tuple[dict, int]:
    try:
        history = HistoryMedical.query.get(id)
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
