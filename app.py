import os

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from analyzer.analysis_service import analyze_message
from analyzer.ml_classifier import get_ml_status


app = Flask(__name__)

app.config["JSON_AS_ASCII"] = False


@app.get("/")
def index():
    return render_template(
        "index.html",
        result=None,
        email_text="",
        error=None,
    )


@app.post("/analyze")
def analyze():
    email_text = request.form.get(
        "email_text",
        "",
    ).strip()

    if not email_text:
        return render_template(
            "index.html",
            result=None,
            email_text="",
            error=(
                "Digite ou cole o conteúdo "
                "de um e-mail."
            ),
        ), 400

    try:
        result = analyze_message(
            email_text
        )

        return render_template(
            "index.html",
            result=result,
            email_text=email_text,
            error=None,
        )

    except Exception as error:
        print(
            "Erro durante a análise: "
            f"{type(error).__name__}: {error!r}"
        )

        return render_template(
            "index.html",
            result=None,
            email_text=email_text,
            error=(
                "Não foi possível realizar a análise. "
                "Verifique o terminal para mais detalhes."
            ),
        ), 500


@app.post("/api/analyze")
def analyze_api():
    request_data = request.get_json(
        silent=True
    ) or {}

    email_text = str(
        request_data.get(
            "email_text",
            "",
        )
    ).strip()

    if not email_text:
        return jsonify(
            {
                "success": False,
                "error": (
                    "O campo 'email_text' "
                    "é obrigatório."
                ),
            }
        ), 400

    try:
        result = analyze_message(
            email_text
        )

        return jsonify(
            {
                "success": True,
                "result": result,
            }
        )

    except Exception as error:
        print(
            "Erro na API de análise: "
            f"{type(error).__name__}: {error!r}"
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Erro interno durante a análise."
                ),
            }
        ), 500


@app.get("/api/ml/status")
def ml_status():
    return jsonify(
        get_ml_status()
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=int(
            os.environ.get(
                "PORT",
                5000,
            )
        ),
    )