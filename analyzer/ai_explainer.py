from ollama import Client

client = Client(host="http://localhost:11434")

MODEL_NAME = "gemma3:4b"


def explain_email(score: int, findings: list[dict]) -> str:
    if not findings:
        return (
            "Nenhum indicador suspeito foi encontrado pelas regras atuais. "
            "Isso não garante que o e-mail seja legítimo."
        )

    summary = "\n".join(
        f"- {finding['message']} (+{finding['score']} pontos)"
        for finding in findings
    )

    prompt = f"""
Você é um assistente educacional especializado em segurança cibernética.

Explique em português simples por que os indicadores abaixo podem estar
relacionados a phishing.

Regras:
- Não invente indicadores.
- Não altere a pontuação.
- Não reproduza URLs.
- Não diga que a classificação é definitiva.
- Escreva no máximo três parágrafos.
- Termine com uma recomendação defensiva.

Pontuação calculada pelo sistema: {score}/100.

Indicadores encontrados:
{summary}
"""

    try:
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0.2,
            },
        )

        return response["message"]["content"]

    except Exception as error:
        return (
            "Não foi possível gerar a explicação com o Ollama. "
            f"Detalhes: {error}"
        )