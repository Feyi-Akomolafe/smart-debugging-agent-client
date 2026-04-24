from flask import Blueprint, render_template, request
from app.services.analyzer import DebugAnalyzer

main = Blueprint("main", __name__)
analyzer = DebugAnalyzer()

@main.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        payload = {
            "error_message": request.form.get("error_message", "").strip(),
            "stack_trace": request.form.get("stack_trace", "").strip(),
            "code_snippet": request.form.get("code_snippet", "").strip(),
            "command_used": request.form.get("command_used", "").strip(),
            "expected_behavior": request.form.get("expected_behavior", "").strip(),
            "actual_behavior": request.form.get("actual_behavior", "").strip(),
            "language": request.form.get("language", "").strip(),
        }
        result = analyzer.analyze(payload)

    return render_template("index.html", result=result)

@main.route("/history")
def history():
    return render_template("history.html", history=analyzer.load_history())
