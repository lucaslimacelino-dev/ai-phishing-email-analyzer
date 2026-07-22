import re
import unicodedata
from collections.abc import Sequence

from analyzer.url_analyzer import analyze_urls


URGENCY_PATTERNS = [
    r"\burgente\b",
    r"\bimediatamente\b",
    r"\bultimo aviso\b",
    r"\bacao necessaria\b",
    r"\bacao imediata\b",
    r"\bsera bloquead[ao]\b",
    r"\bsera suspens[ao]\b",
    r"\bsera encerrad[ao]\b",
    r"\bconta bloqueada\b",
    r"\bconta suspensa\b",
    r"\bprazo expir(?:a|ou|ando)\b",
    r"\bexpira hoje\b",
    r"\bdentro de \d+ horas?\b",
    r"\bagora\b",
    r"\bnao ignore\b",
]

CREDENTIAL_PATTERNS = [
    r"\bsenha\b",
    r"\bcredenciais\b",
    r"\bnome de usuario\b",
    r"\busuario e senha\b",
    r"\bfaca login\b",
    r"\binicie sessao\b",
    r"\bconfirme sua conta\b",
    r"\bconfirme seus dados\b",
    r"\batualize seus dados\b",
    r"\bverifique sua identidade\b",
    r"\bcodigo de acesso\b",
    r"\bcodigo de verificacao\b",
    r"\bcodigo enviado por sms\b",
    r"\btoken de seguranca\b",
    r"\bautenticacao\b",
]

SENSITIVE_DATA_PATTERNS = [
    r"\bcpf\b",
    r"\brg\b",
    r"\bdata de nascimento\b",
    r"\bendereco completo\b",
    r"\bnumero do cartao\b",
    r"\bcodigo de seguranca\b",
    r"\bcvv\b",
    r"\bchave pix\b",
    r"\bdados pessoais\b",
    r"\bdados bancarios\b",
]

FINANCIAL_PATTERNS = [
    r"\bcartao\b",
    r"\bconta bancaria\b",
    r"\bpix\b",
    r"\bpagamento\b",
    r"\btaxa\b",
    r"\bboleto\b",
    r"\btransferencia\b",
    r"\bfatura\b",
    r"\breembolso\b",
    r"\bdeposito\b",
    r"\bdebito\b",
    r"\bcredito\b",
]

REWARD_PATTERNS = [
    r"\bvoce ganhou\b",
    r"\bfoi selecionad[ao]\b",
    r"\bpremio\b",
    r"\brecompensa\b",
    r"\bsorteio\b",
    r"\boferta exclusiva\b",
    r"\bdinheiro gratis\b",
    r"\bbrinde\b",
    r"\bresgate seu premio\b",
    r"\bparabens\b.{0,30}\bganhou\b",
]

THREAT_PATTERNS = [
    r"\bsua conta sera\b",
    r"\bseu acesso sera\b",
    r"\bsera aplicada uma multa\b",
    r"\bmedidas legais\b",
    r"\batividade suspeita\b",
    r"\bacesso nao autorizado\b",
    r"\btentativa de login\b",
    r"\bcompra nao reconhecida\b",
    r"\btransacao suspeita\b",
    r"\bproblema de seguranca\b",
]

ACTION_PATTERNS = [
    r"\bclique aqui\b",
    r"\bclique no link\b",
    r"\bacesse o link\b",
    r"\babra o link\b",
    r"\bpressione o botao\b",
    r"\bconfirme agora\b",
    r"\bverifique agora\b",
    r"\bresgate agora\b",
    r"\bpreencha o formulario\b",
    r"\bbaixe o arquivo\b",
    r"\babra o anexo\b",
    r"\bgo to (?:the )?web-?site\b",
    r"\bcheck for yourself\b",
    r"\bvisit (?:our|the) website\b",
]

ATTACHMENT_PATTERNS = [
    r"\b[\w.-]+\.(?:exe|scr|bat|cmd|com|msi|ps1|vbs|js|jar)\b",
    r"\b[\w.-]+\.(?:zip|rar|7z|iso)\b",
    r"\bfatura\.(?:zip|rar|exe|html?)\b",
    r"\bboleto\.(?:zip|rar|exe|html?)\b",
    r"\bcomprovante\.(?:zip|rar|exe|html?)\b",
    r"\bnota[_ -]?fiscal\.(?:zip|rar|exe|html?)\b",
    r"\banexo protegido por senha\b",
    r"\barquivo protegido por senha\b",
    r"\bhabilite as macros\b",
    r"\bative o conteudo\b",
]

IMPERSONATION_PATTERNS = [
    r"\bsuporte tecnico\b",
    r"\bequipe de seguranca\b",
    r"\bdepartamento financeiro\b",
    r"\bcentral de atendimento\b",
    r"\badministrador(?:a)? do sistema\b",
    r"\bservico de seguranca\b",
    r"\breceita federal\b",
    r"\bbanco central\b",
    r"\bcorreios\b",
]

SPAM_PATTERNS = [
    r"\boferta imperdivel\b",
    r"\bpromocao\b",
    r"\bcompre agora\b",
    r"\bresultado garantido\b",
    r"\bdesconto de \d+%\b",
    r"\bfrete gratis\b",
    r"\bultimas unidades\b",
    r"\bcupom exclusivo\b",

    # Inglês
    r"\blowest prices\b",
    r"\bbelow retail price\b",
    r"\bfree delivery\b",
    r"\bjoin (?:us|them)\b",
    r"\bonline store\b",
    r"\bhigh-quality\b",
    r"\bguarantee\b",
    r"\bclients over the whole world\b",
]

GENERIC_GREETING_PATTERNS = [
    r"\bprezado cliente\b",
    r"\bcaro usuario\b",
    r"\bestimado cliente\b",
    r"\bcliente\b",
    r"\busuario\b",
]

HTML_FORM_PATTERNS = [
    r"<form\b",
    r"<input\b[^>]*type=[\"']?(?:password|email)",
    r"<button\b",
    r"<iframe\b",
    r"javascript\s*:",
]

OBFUSCATION_PATTERNS = [
    r"\bhxxps?://",
    r"\bhttps?\s*:\s*/\s*/",
    r"\[\s*dot\s*\]",
    r"\(\s*dot\s*\)",
    r"\bbit\s*\.\s*ly\b",
    r"\btinyurl\s*\.\s*com\b",
    r"\bcutt\s*\.\s*ly\b",
]


def normalize_text(text: str) -> str:
    """
    Converte o texto para minúsculas e remove acentos.

    Isso permite que os padrões detectem, por exemplo,
    tanto 'urgente' quanto palavras acentuadas sem precisar
    duplicar expressões regulares.
    """
    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return without_accents.lower()


def find_pattern_matches(
    text: str,
    patterns: Sequence[str],
) -> list[str]:
    """
    Retorna os padrões que apareceram no texto.

    Cada padrão é contado apenas uma vez, mesmo que apareça
    repetidamente na mensagem.
    """
    return [
        pattern
        for pattern in patterns
        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
    ]


def count_pattern_matches(
    text: str,
    patterns: Sequence[str],
) -> int:
    return len(
        find_pattern_matches(
            text,
            patterns,
        )
    )


def add_finding(
    findings: list[str],
    message: str,
) -> None:
    """
    Adiciona um indicador sem repetir mensagens iguais.
    """
    if message not in findings:
        findings.append(message)


def calculate_risk_level(
    score: int,
) -> str:
    if score >= 75:
        return "Crítico"

    if score >= 50:
        return "Alto"

    if score >= 25:
        return "Médio"

    return "Baixo"


def analyze_email(
    email_text: str,
) -> dict:
    if not isinstance(email_text, str):
        email_text = str(
            email_text or ""
        )

    normalized_text = normalize_text(
        email_text
    )

    findings: list[str] = []
    categories: list[str] = []
    score_breakdown: dict[str, int] = {}

    score = 0

    def add_score(
        category: str,
        value: int,
        finding: str | None = None,
    ) -> None:
        nonlocal score

        if value <= 0:
            return

        score += value
        score_breakdown[category] = (
            score_breakdown.get(category, 0)
            + value
        )

        if category not in categories:
            categories.append(category)

        if finding:
            add_finding(
                findings,
                finding,
            )

    # ---------------------------------------------------------
    # Análise de URLs
    # ---------------------------------------------------------

    url_result = analyze_urls(
        email_text
    )

    urls = url_result.get(
        "urls",
        [],
    )

    url_findings = url_result.get(
        "findings",
        [],
    )

    url_score = int(
        url_result.get(
            "score",
            0,
        )
        or 0
    )

    if urls:
        add_score(
            "URLs",
            5,
            (
                f"{len(urls)} URL(s) "
                "encontrada(s) na mensagem."
            ),
        )

    if url_findings:
        for url_finding in url_findings:
            add_finding(
                findings,
                url_finding,
            )

        # O analisador de URLs é responsável pelos detalhes.
        # Aqui a pontuação é limitada para evitar dominar o resultado.
        add_score(
            "URLs suspeitas",
            min(url_score, 35),
        )

    # ---------------------------------------------------------
    # Contagem dos grupos de padrões
    # ---------------------------------------------------------

    urgency_count = count_pattern_matches(
        normalized_text,
        URGENCY_PATTERNS,
    )

    credential_count = count_pattern_matches(
        normalized_text,
        CREDENTIAL_PATTERNS,
    )

    sensitive_data_count = count_pattern_matches(
        normalized_text,
        SENSITIVE_DATA_PATTERNS,
    )

    financial_count = count_pattern_matches(
        normalized_text,
        FINANCIAL_PATTERNS,
    )

    reward_count = count_pattern_matches(
        normalized_text,
        REWARD_PATTERNS,
    )

    threat_count = count_pattern_matches(
        normalized_text,
        THREAT_PATTERNS,
    )

    action_count = count_pattern_matches(
        normalized_text,
        ACTION_PATTERNS,
    )

    attachment_count = count_pattern_matches(
        normalized_text,
        ATTACHMENT_PATTERNS,
    )

    impersonation_count = count_pattern_matches(
        normalized_text,
        IMPERSONATION_PATTERNS,
    )

    spam_count = count_pattern_matches(
        normalized_text,
        SPAM_PATTERNS,
    )

    generic_greeting_count = count_pattern_matches(
        normalized_text,
        GENERIC_GREETING_PATTERNS,
    )

    html_form_count = count_pattern_matches(
        email_text,
        HTML_FORM_PATTERNS,
    )

    obfuscation_count = count_pattern_matches(
        normalized_text,
        OBFUSCATION_PATTERNS,
    )

    # ---------------------------------------------------------
    # Pontuações individuais
    # ---------------------------------------------------------

    if urgency_count:
        urgency_score = min(
            6 + (urgency_count - 1) * 3,
            15,
        )

        add_score(
            "Urgência",
            urgency_score,
            "A mensagem utiliza linguagem de urgência ou pressão.",
        )

    if credential_count:
        credential_score = min(
            15 + (credential_count - 1) * 4,
            27,
        )

        add_score(
            "Credenciais",
            credential_score,
            (
                "A mensagem solicita ou menciona "
                "credenciais de acesso."
            ),
        )

    if sensitive_data_count:
        sensitive_score = min(
            12 + (sensitive_data_count - 1) * 4,
            24,
        )

        add_score(
            "Dados sensíveis",
            sensitive_score,
            (
                "A mensagem solicita ou menciona "
                "dados pessoais sensíveis."
            ),
        )

    if financial_count:
        # Termos financeiros isolados são comuns em mensagens legítimas.
        financial_score = min(
            4 + (financial_count - 1) * 3,
            13,
        )

        add_score(
            "Conteúdo financeiro",
            financial_score,
            (
                "A mensagem menciona informações "
                "ou operações financeiras."
            ),
        )

    if reward_count:
        reward_score = min(
            8 + (reward_count - 1) * 3,
            17,
        )

        add_score(
            "Promessa de recompensa",
            reward_score,
            (
                "A mensagem utiliza promessa de "
                "prêmio, benefício ou recompensa."
            ),
        )

    if threat_count:
        threat_score = min(
            8 + (threat_count - 1) * 3,
            17,
        )

        add_score(
            "Ameaça ou medo",
            threat_score,
            (
                "A mensagem menciona bloqueio, atividade suspeita "
                "ou outra possível ameaça."
            ),
        )

    if action_count:
        action_score = min(
            4 + (action_count - 1) * 2,
            10,
        )

        add_score(
            "Indução à ação",
            action_score,
            (
                "A mensagem tenta induzir o usuário "
                "a realizar uma ação."
            ),
        )

    if attachment_count:
        attachment_score = min(
            15 + (attachment_count - 1) * 5,
            25,
        )

        add_score(
            "Anexo suspeito",
            attachment_score,
            (
                "A mensagem menciona um anexo, extensão "
                "ou instrução potencialmente perigosa."
            ),
        )

    if impersonation_count:
        impersonation_score = min(
            4 + (impersonation_count - 1) * 2,
            10,
        )

        add_score(
            "Possível personificação",
            impersonation_score,
            (
                "A mensagem aparenta representar uma instituição "
                "ou departamento de confiança."
            ),
        )

    if html_form_count:
        html_score = min(
            12 + (html_form_count - 1) * 4,
            24,
        )

        add_score(
            "Formulário HTML",
            html_score,
            (
                "O conteúdo possui elementos HTML que podem "
                "ser usados para coletar informações."
            ),
        )

    if obfuscation_count:
        obfuscation_score = min(
            10 + (obfuscation_count - 1) * 4,
            22,
        )

        add_score(
            "Ofuscação",
            obfuscation_score,
            (
                "A mensagem apresenta endereço ou conteúdo "
                "escrito de forma ofuscada."
            ),
        )

    # Spam comum deve ter peso baixo para não ser automaticamente
    # tratado como phishing.
    if spam_count:
        spam_score = min(
            3 + (spam_count - 1) * 2,
            9,
        )

        add_score(
            "Linguagem promocional",
            spam_score,
            (
                "A mensagem contém linguagem promocional "
                "típica de spam."
            ),
        )

    if generic_greeting_count:
        add_score(
            "Saudação genérica",
            3,
            (
                "A mensagem utiliza uma saudação genérica "
                "em vez de identificar o destinatário."
            ),
        )

    # ---------------------------------------------------------
    # Características de escrita
    # ---------------------------------------------------------

    exclamation_count = email_text.count("!")

    if exclamation_count >= 8:
        add_score(
            "Pontuação excessiva",
            8,
            (
                "A mensagem utiliza quantidade excessiva "
                "de pontos de exclamação."
            ),
        )

    elif exclamation_count >= 3:
        add_score(
            "Pontuação excessiva",
            4,
            (
                "A mensagem utiliza vários pontos "
                "de exclamação."
            ),
        )

    uppercase_words = re.findall(
        r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{4,}\b",
        email_text,
    )

    uppercase_count = len(
        uppercase_words
    )

    if uppercase_count >= 8:
        add_score(
            "Uso excessivo de maiúsculas",
            8,
            (
                "A mensagem utiliza muitas palavras "
                "escritas em letras maiúsculas."
            ),
        )

    elif uppercase_count >= 4:
        add_score(
            "Uso excessivo de maiúsculas",
            4,
            (
                "A mensagem utiliza quantidade incomum "
                "de palavras em maiúsculas."
            ),
        )

    repeated_punctuation = re.search(
        r"[!?]{4,}",
        email_text,
    )

    if repeated_punctuation:
        add_score(
            "Pontuação repetida",
            4,
            (
                "A mensagem utiliza sinais de pontuação "
                "repetidos de forma incomum."
            ),
        )

    # ---------------------------------------------------------
    # Combinações de alto risco
    # ---------------------------------------------------------

    # Solicitar senha e oferecer um link é mais suspeito
    # do que cada característica separadamente.
    if credential_count and urls:
        add_score(
            "Combinação crítica",
            15,
            (
                "A mensagem combina solicitação de credenciais "
                "com a presença de link."
            ),
        )

    if sensitive_data_count and urls:
        add_score(
            "Combinação crítica",
            12,
            (
                "A mensagem combina solicitação de dados "
                "sensíveis com a presença de link."
            ),
        )

    if urgency_count and action_count:
        add_score(
            "Pressão para ação",
            8,
            (
                "A mensagem combina urgência com uma "
                "solicitação direta de ação."
            ),
        )

    if threat_count and action_count:
        add_score(
            "Ameaça com ação",
            8,
            (
                "A mensagem utiliza uma ameaça para convencer "
                "o usuário a realizar uma ação."
            ),
        )

    if financial_count and action_count and urls:
        add_score(
            "Fraude financeira potencial",
            10,
            (
                "A mensagem combina tema financeiro, link "
                "e solicitação de ação."
            ),
        )

    if reward_count and action_count and urls:
        add_score(
            "Recompensa com link",
            9,
            (
                "A mensagem combina promessa de recompensa "
                "com um link e solicitação de ação."
            ),
        )

    if impersonation_count and credential_count:
        add_score(
            "Personificação com credenciais",
            9,
            (
                "A mensagem aparenta representar uma instituição "
                "e solicita credenciais."
            ),
        )

    if html_form_count and credential_count:
        add_score(
            "Coleta de credenciais",
            15,
            (
                "O conteúdo combina formulário HTML "
                "com solicitação de credenciais."
            ),
        )

    # ---------------------------------------------------------
    # Resultado
    # ---------------------------------------------------------

    score = min(
        max(score, 0),
        100,
    )

    return {
        "score": score,
        "risk_score": score,
        "risk_level": calculate_risk_level(
            score
        ),
        "findings": findings,
        "categories": categories,
        "score_breakdown": score_breakdown,
        "urls": urls,
        "url_analyses": url_result.get(
            "analyses",
            [],
        ),
        "metrics": {
            "urgency_matches": urgency_count,
            "credential_matches": credential_count,
            "sensitive_data_matches": sensitive_data_count,
            "financial_matches": financial_count,
            "reward_matches": reward_count,
            "threat_matches": threat_count,
            "action_matches": action_count,
            "attachment_matches": attachment_count,
            "impersonation_matches": impersonation_count,
            "spam_matches": spam_count,
            "html_form_matches": html_form_count,
            "obfuscation_matches": obfuscation_count,
            "exclamation_count": exclamation_count,
            "uppercase_word_count": uppercase_count,
        },
    }