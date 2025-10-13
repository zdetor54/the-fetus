# chatai/views.py
from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import login_required

from fetusapp import csrf  # type: ignore[has-type]
from fetusapp.chatai.services import run_agent

chatai = Blueprint("chatai", __name__)


@chatai.route("/chat")
def chat() -> Response:
    """Render the chat page with chatbot UI"""
    return render_template("chat.html")


@chatai.route("/chat/api", methods=["POST"])
@login_required
@csrf.exempt
def chat_api() -> Response:
    """
    API endpoint that processes chat questions.
    The frontend (chat.html) will call this endpoint.

    Expected JSON:
    {
        "question": "Ποιοι ασθενείς είναι γιατροί;"
    }

    Returns JSON:
    {
        "question": "...",
        "answer": "..."
    }
    """
    try:
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        question = data["question"]

        # Run the agent (already in app context since this is a Flask route)
        answer = run_agent(question)

        return jsonify({"question": question, "answer": answer}), 200

    except Exception as e:
        return jsonify({"error": f"Σφάλμα: {str(e)}"}), 500
