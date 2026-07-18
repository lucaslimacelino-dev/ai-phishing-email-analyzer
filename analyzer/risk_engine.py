from dataclasses import dataclass, field

from analyzer.url_analyzer import analyze_url, extract_urls


@dataclass
class AnalysisResult:
    score: int
    risk_level: str
    findings: list[dict] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)


KEYWORD_RULES = [
    {
        "indicator": "urgent_language",
        "terms": [
            "urgente",
            "imediatamente",
            "última chance",
            "conta será bloqueada",
        ],
        "score": 10,
        "message": "O texto utiliza linguagem de urgência ou pressão.",
    },
    {
        "indicator": "credential_request",
        "terms": [
            "confirme sua senha",
            "verifique sua conta",
            "atualize seus dados",
            "faça login",
        ],
        "score": 20,
        "message": "O texto aparenta solicitar credenciais ou dados pessoais.",
    },
    {
        "indicator": "financial_request",
        "terms": [
            "pagamento pendente",
            "transferência",
            "reembolso",
            "prêmio",
        ],
        "score": 12,
        "message": "O texto contém uma solicitação ou promessa financeira.",
    },
]


def get_risk_level(score: int) -> str:
    if score >= 60:
        return "Alto"
    if score >= 30:
        return "Médio"
    return "Baixo"


def analyze_email(text: str) -> AnalysisResult:
    normalized_text = text.casefold()
    findings: list[dict] = []

    for rule in KEYWORD_RULES:
        matched_terms = [
            term for term in rule["terms"]
            if term.casefold() in normalized_text
        ]

        if matched_terms:
            findings.append({
                "indicator": rule["indicator"],
                "score": rule["score"],
                "message": rule["message"],
                "evidence": matched_terms,
            })

    urls = extract_urls(text)

    for url in urls:
        for url_finding in analyze_url(url):
            findings.append({
                **url_finding,
                "evidence": url,
            })

    score = min(sum(item["score"] for item in findings), 100)

    return AnalysisResult(
        score=score,
        risk_level=get_risk_level(score),
        findings=findings,
        urls=urls,
    )