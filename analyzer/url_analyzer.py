import re
from urllib.parse import urlparse


URL_PATTERN = re.compile(
    r"""
    (?:
        https?://
        |
        www\.
    )
    [^\s<>"')\]]+
    """,
    re.IGNORECASE | re.VERBOSE,
)


SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
}


def extract_urls(text: str) -> list[str]:
    if not isinstance(text, str):
        return []

    urls = URL_PATTERN.findall(text)

    cleaned_urls = []

    for url in urls:
        cleaned_url = url.rstrip(
            ".,;:!?)]}>"
        )

        if cleaned_url not in cleaned_urls:
            cleaned_urls.append(cleaned_url)

    return cleaned_urls


def analyze_url(url: str) -> dict:
    normalized_url = url

    if normalized_url.startswith("www."):
        normalized_url = f"http://{normalized_url}"

    parsed = urlparse(normalized_url)

    domain = parsed.netloc.lower()

    if ":" in domain:
        domain = domain.split(":")[0]

    findings = []
    score = 0

    if normalized_url.startswith("http://"):
        findings.append(
            "A URL utiliza HTTP sem criptografia."
        )
        score += 15

    if domain in SHORTENER_DOMAINS:
        findings.append(
            "A mensagem utiliza um encurtador de URL."
        )
        score += 20

    if re.fullmatch(
        r"\d{1,3}(?:\.\d{1,3}){3}",
        domain,
    ):
        findings.append(
            "A URL utiliza um endereço IP no lugar de um domínio."
        )
        score += 25

    if "@" in url:
        findings.append(
            "A URL contém o caractere @, que pode ocultar o destino real."
        )
        score += 20

    if domain.count("-") >= 3:
        findings.append(
            "O domínio possui uma quantidade incomum de hífens."
        )
        score += 10

    if len(url) > 150:
        findings.append(
            "A URL é excessivamente longa."
        )
        score += 10

    return {
        "url": url,
        "domain": domain,
        "score": min(score, 100),
        "findings": findings,
    }


def analyze_urls(text: str) -> dict:
    urls = extract_urls(text)

    analyses = [
        analyze_url(url)
        for url in urls
    ]

    findings = []

    for analysis in analyses:
        findings.extend(
            analysis["findings"]
        )

    return {
        "urls": urls,
        "analyses": analyses,
        "findings": findings,
        "score": min(
            sum(
                analysis["score"]
                for analysis in analyses
            ),
            100,
        ),
    }