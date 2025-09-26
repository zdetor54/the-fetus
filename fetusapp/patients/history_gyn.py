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


# @pregnancy.route("/api/pregnancy", methods=["POST"])
# @login_required
# @csrf.exempt
# def create_pregnancy_history() -> tuple[dict, int]:
#     try:
#         payload = request.get_json(silent=True) or {}
#         patient_id = payload.get("patient_id")
#         print("Patient ID:", patient_id)
#         if not patient_id:
#             return jsonify({"success": False, "error": "Missing patient_id"}), 400

#         form = PregnancyHistoryEntryForm(data=payload)

#         # Remove 'id' from payload for creation (let DB handle it)
#         if "id" in payload:
#             del payload["id"]

#         # Set required system fields
#         payload["patient_id"] = patient_id
#         payload["created_by"] = current_user.id
#         payload["last_updated_by"] = current_user.id

#         if form.validate():
#             new_history = PregnancyHistory(
#                 patient_id=patient_id,
#                 created_by=current_user.id,
#                 last_updated_by=current_user.id,
#             )

#             for field in form._fields:
#                 if field not in [
#                     "csrf_token",
#                     "submit",
#                     "patient_id",
#                     "created_by",
#                     "last_updated_by",
#                 ]:
#                     if field in payload:
#                         setattr(new_history, field, form._fields[field].data)

#             new_history.created_by = current_user.id
#             new_history.created_on = datetime.utcnow()
#             new_history.last_updated_by = current_user.id
#             new_history.last_updated_on = datetime.utcnow()

#             db.session.add(new_history)
#             db.session.commit()
#             return jsonify({"success": True, "id": new_history.id}), 201
#         else:
#             return jsonify({"success": False, "errors": form.errors}), 400
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 400


# @pregnancy.route("/api/pregnancy/<int:id>", methods=["DELETE"])
# @login_required
# @csrf.exempt
# def delete_pregnancy(id: int) -> tuple[dict, int]:
#     try:
#         history = PregnancyHistory.query.get_or_404(id)
#         if not history:
#             return (
#                 jsonify({"success": False, "error": "Pregnancy not found"}),
#                 404,
#             )
#         # Soft delete: mark as inactive and update metadata
#         history.is_active = False
#         history.last_updated_by = current_user.id
#         history.last_updated_on = datetime.utcnow()
#         db.session.commit()
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 400


# @pregnancy.route("/api/pregnancy-x/<int:id>", methods=["PUT"])
# @login_required
# @csrf.exempt
# def update_pregnancy_x(id: int) -> tuple[dict, int]:
#     try:
#         # Get existing record
#         history = PregnancyHistory_x.query.get_or_404(id)
#         pregnancy = PregnancyHistory.query.get(history.pregnancy_id)
#         ter = None
#         if not pregnancy:
#             return jsonify({"success": False, "error": "Missing pregnancy"}), 400
#         else:
#             ter = pregnancy.ter

#         # Read and normalize JSON payload so WTForms validators accept booleans
#         payload = request.get_json(silent=True) or {}

#         form = PregnancyHistoryXEntryForm(data=payload)

#         if form.validate():
#             # Update history fields from form data
#             for field in form._fields:
#                 if field not in ["csrf_token", "submit"]:
#                     if field in payload:
#                         value = form._fields[field].data
#                         if value != "" and value is not None:
#                             setattr(history, field, value)
#                         else:
#                             setattr(history, field, None)
#             history.pregnancy_age = calculate_pregnancy_age(ter, history.date_of_visit)
#             history.last_updated_by = current_user.id
#             history.last_updated_on = datetime.utcnow()

#             # print(f"Updated pregnancy history: {history.to_dict()}")

#             db.session.commit()
#             return jsonify({"success": True}), 200
#         else:
#             return jsonify({"success": False, "errors": form.errors}), 400
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 400


# @pregnancy.route("/api/pregnancy-x/<int:pregnancy_id>", methods=["POST"])
# @login_required
# @csrf.exempt
# def create_pregnancy_history_x(pregnancy_id: int) -> tuple[dict, int]:
#     try:
#         payload = request.get_json(silent=True) or {}
#         pregnancy = PregnancyHistory.query.get(pregnancy_id)
#         ter = None
#         if not pregnancy:
#             return jsonify({"success": False, "error": "Missing pregnancy"}), 400
#         else:
#             ter = pregnancy.ter

#         form = PregnancyHistoryXEntryForm(data=payload)

#         # Remove 'id' from payload for creation (let DB handle it)
#         if "id" in payload:
#             del payload["id"]

#         # Set required system fields
#         payload["pregnancy_id"] = pregnancy_id
#         payload["created_by"] = current_user.id
#         payload["last_updated_by"] = current_user.id

#         if form.validate():
#             new_history = PregnancyHistory_x(
#                 pregnancy_id=pregnancy_id,
#                 created_by=current_user.id,
#                 last_updated_by=current_user.id,
#             )

#             for field in form._fields:
#                 if field not in [
#                     "csrf_token",
#                     "submit",
#                     "pregnancy_id",
#                     "created_by",
#                     "last_updated_by",
#                 ]:
#                     if field in payload:
#                         setattr(new_history, field, form._fields[field].data)
#             new_history.pregnancy_age = calculate_pregnancy_age(
#                 ter, new_history.date_of_visit
#             )

#             new_history.created_by = current_user.id
#             new_history.created_on = datetime.utcnow()
#             new_history.last_updated_by = current_user.id
#             new_history.last_updated_on = datetime.utcnow()

#             db.session.add(new_history)
#             db.session.commit()
#             return jsonify({"success": True, "id": new_history.id}), 201
#         else:
#             return jsonify({"success": False, "errors": form.errors}), 400
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 400


# @pregnancy.route("/api/pregnancy-x/<int:id>", methods=["DELETE"])
# @login_required
# @csrf.exempt
# def delete_pregnancy_x(id: int) -> tuple[dict, int]:
#     try:
#         history = PregnancyHistory_x.query.get_or_404(id)
#         if not history:
#             return (
#                 jsonify({"success": False, "error": "Pregnancy not found"}),
#                 404,
#             )
#         # Soft delete: mark as inactive and update metadata
#         history.is_active = False
#         history.last_updated_by = current_user.id
#         history.last_updated_on = datetime.utcnow()
#         db.session.commit()
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 400
