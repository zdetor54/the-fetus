from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import HistoryMedical

from .forms import HistoryMedicalForm

medical_history = Blueprint("medical_history", __name__)


@medical_history.route("/api/medical-history/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_medical_history(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = HistoryMedical.query.get_or_404(id)

        # Read and normalize JSON payload so WTForms validators accept radios/booleans
        payload = request.get_json(silent=True) or {}

        form = HistoryMedicalForm(data=payload)

        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        setattr(history, field, form._fields[field].data)

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
