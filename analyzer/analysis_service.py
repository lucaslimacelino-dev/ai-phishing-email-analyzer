from typing import Any

from analyzer.ml_classifier import classify_email
from analyzer.n8n_client import request_ai_comment
from analyzer.risk_engine import analyze_email


def extract_rule_score(
    rule_result: dict[str, Any],
) -> float:
    """
    Procura o score do motor de regras usando nomes comuns.

    Isso evita quebrar a integração caso o risk_engine use
    'score', 'risk_score' ou outro nome semelhante.
    """

    possible_keys = (
        "risk_score",
        "score",
        "percentage",
        "risk_percentage",
    )

    for key in possible_keys:
        value = rule_result.get(key)

        if isinstance(value, (int, float)):
            return max(
                0.0,
                min(float(value), 100.0),
            )

    return 0.0


def calculate_final_score(
    rule_score: float,
    ml_result: dict[str, Any],
) -> int:
    """
    Combina o motor de regras com o Machine Learning.

    Um resultado inconclusivo do ML não aumenta o score.
    """

    if not ml_result.get("available"):
        return round(rule_score)

    classification = ml_result.get(
        "classification"
    )

    if classification == "Inconclusivo":
        return round(rule_score)

    ml_score = float(
        ml_result.get("risk_score") or 0
    )

    final_score = (
        rule_score * 0.60
        + ml_score * 0.40
    )

    return round(
        max(
            0.0,
            min(final_score, 100.0),
        )
    )


def classify_risk_level(
    score: int,
) -> str:
    if score >= 75:
        return "Crítico"

    if score >= 50:
        return "Alto"

    if score >= 25:
        return "Médio"

    return "Baixo"


def create_n8n_payload(
    email_text: str,
    rule_result: dict[str, Any],
    rule_score: int,
    ml_result: dict[str, Any],
    final_score: int,
    risk_level: str,
) -> dict[str, Any]:
    """
    Monta apenas os dados necessários para o n8n e o Gemini.

    O Gemini recebe o resultado pronto e deve apenas comentá-lo.
    """

    return {
        "email_text": email_text,
        "rule_score": rule_score,
        "rule_risk_level": rule_result.get(
            "risk_level"
        ),
        "findings": rule_result.get(
            "findings",
            [],
        ),
        "categories": rule_result.get(
            "categories",
            [],
        ),
        "score_breakdown": rule_result.get(
            "score_breakdown",
            {},
        ),
        "urls": rule_result.get(
            "urls",
            [],
        ),
        "ml_available": ml_result.get(
            "available",
            False,
        ),
        "ml_classification": ml_result.get(
            "classification"
        ),
        "phishing_probability": ml_result.get(
            "phishing_probability"
        ),
        "legitimate_probability": ml_result.get(
            "legitimate_probability"
        ),
        "final_score": final_score,
        "risk_level": risk_level,
    }


def analyze_message(
    email_text: str,
) -> dict[str, Any]:
    """
    Executa toda a análise da aplicação.

    Componentes obrigatórios:
    - motor de regras;
    - cálculo do resultado principal.

    Componentes opcionais:
    - Machine Learning;
    - n8n e Gemini.
    """

    rule_result = analyze_email(
        email_text
    )

    if not isinstance(rule_result, dict):
        rule_result = {
            "result": rule_result,
            "findings": [],
            "urls": [],
        }

    ml_result = classify_email(
        email_text
    )

    if not isinstance(ml_result, dict):
        ml_result = {
            "available": False,
            "classification": None,
            "phishing_probability": None,
            "legitimate_probability": None,
            "risk_score": 0,
        }

    rule_score = extract_rule_score(
        rule_result
    )

    final_score = calculate_final_score(
        rule_score=rule_score,
        ml_result=ml_result,
    )

    risk_level = classify_risk_level(
        final_score
    )

    n8n_payload = create_n8n_payload(
        email_text=email_text,
        rule_result=rule_result,
        rule_score=round(rule_score),
        ml_result=ml_result,
        final_score=final_score,
        risk_level=risk_level,
    )

    # Esta chamada nunca deve impedir a análise principal.
    ai_analysis = request_ai_comment(
        n8n_payload
    )

    return {
        "email_text": email_text,
        "rule_analysis": rule_result,
        "rule_score": round(rule_score),
        "ml_analysis": ml_result,
        "ml_available": ml_result.get(
            "available",
            False,
        ),
        "final_score": final_score,
        "risk_level": risk_level,
        "analysis_mode": (
            "Regras + Machine Learning"
            if ml_result.get("available")
            else "Somente motor de regras"
        ),
        "ai_analysis": ai_analysis,
    }