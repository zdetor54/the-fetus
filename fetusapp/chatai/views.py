from flask import Blueprint, Response, render_template

chatai = Blueprint("chatai", __name__)


@chatai.route("/chat")
def chat() -> Response:
    return render_template("chat.html")
