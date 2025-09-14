from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from fetusapp import csrf, db  # type: ignore[has-type]
from fetusapp.models import PregnancyHistory, PregnancyHistory_x

from .forms import PregnancyHistoryEntryForm, PregnancyHistoryXEntryForm

pregnancy = Blueprint("pregnancy", __name__)
pregnancy_x = Blueprint("pregnancy_x", __name__)


@pregnancy.route("/api/pregnancy/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_pregnancy(id: int) -> tuple[dict, int]:
    try:
        # Get existing record
        history = PregnancyHistory.query.get_or_404(id)

        # Read and normalize JSON payload so WTForms validators accept booleans
        payload = request.get_json(silent=True) or {}

        form = PregnancyHistoryEntryForm(data=payload)

        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ["csrf_token", "submit"]:
                    if field in payload:
                        setattr(history, field, form._fields[field].data)

            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()

            print(f"Updated pregnancy history: {history.to_dict()}")

            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "errors": form.errors}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
