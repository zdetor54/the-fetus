from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from fetusapp import db
from fetusapp.models import HistoryMedical
from .forms import HistoryMedicalForm

medical_history = Blueprint('medical_history', __name__)

@medical_history.route('/api/medical-history/<int:id>', methods=['PUT'])
@login_required
def update_medical_history(id):
    try:
        # Get existing record
        history = HistoryMedical.query.get_or_404(id)
        
        # Create form with request data
        form = HistoryMedicalForm(data=request.get_json())
        
        if form.validate():
            # Update history fields from form data
            for field in form._fields:
                if field not in ['csrf_token', 'submit']:
                    setattr(history, field, form._fields[field].data)
            
            # Update metadata
            history.last_updated_by = current_user.id
            history.last_updated_on = datetime.utcnow()

            # preserve the original created_by and created_on fields as well as the patient_id
        
            
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            return jsonify({
                'success': False, 
                'errors': form.errors
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 400