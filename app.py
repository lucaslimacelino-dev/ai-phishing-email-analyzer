from flask import Flask, render_template, request

from analyzer.ai_explainer import explain_email
from analyzer.risk_engine import analyze_email

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    explanation = None
    email_text = ""
    use_ai = False

    if request.method == "POST":
        email_text = request.form.get("email_text", "").strip()
        use_ai = request.form.get("use_ai") == "on"

        if email_text:
            result = analyze_email(email_text)

            if use_ai:
                explanation = explain_email(
                    result.score,
                    result.findings
                )

    return render_template(
        "index.html",
        result=result,
        explanation=explanation,
        email_text=email_text,
        use_ai=use_ai
    )


if __name__ == "__main__":
    app.run(debug=True)