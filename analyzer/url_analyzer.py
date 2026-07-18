import ipaddress
import re
from urllib.parse import urlsplit

URL_PATTERN = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
}


def extract_urls(text: str) -> list[str]:
    """Extrai URLs HTTP/HTTPS sem acessá-las."""
    return URL_PATTERN.findall(text)


def is_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def analyze_url(url: str) -> list[dict]:
    findings: list[dict] = []

    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").lower()
    except ValueError:
        return [{
            "indicator": "malformed_url",
            "score": 15,
            "message": "A URL possui uma estrutura inválida.",
        }]

    if not hostname:
        findings.append({
            "indicator": "missing_hostname",
            "score": 20,
            "message": "Não foi possível identificar o domínio da URL.",
        })
        return findings

    if is_ip_address(hostname):
        findings.append({
            "indicator": "ip_address_url",
            "score": 25,
            "message": "A URL usa um endereço IP no lugar de um domínio.",
        })

    if hostname in SHORTENER_DOMAINS:
        findings.append({
            "indicator": "shortened_url",
            "score": 12,
            "message": "A URL utiliza um serviço de encurtamento.",
        })

    if parsed.scheme == "http":
        findings.append({
            "indicator": "unencrypted_url",
            "score": 8,
            "message": "A URL utiliza HTTP em vez de HTTPS.",
        })

    if hostname.count(".") >= 4:
        findings.append({
            "indicator": "many_subdomains",
            "score": 10,
            "message": "O domínio contém uma quantidade incomum de subdomínios.",
        })

    if "@" in url:
        findings.append({
            "indicator": "at_symbol_url",
            "score": 15,
            "message": "A URL contém o caractere @, que pode ocultar o destino.",
        })

    if len(url) > 150:
        findings.append({
            "indicator": "long_url",
            "score": 7,
            "message": "A URL é excepcionalmente longa.",
        })

    return findings