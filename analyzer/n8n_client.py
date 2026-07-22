import os
from typing import Any

import requests


DEFAULT_TIMEOUT = 8


def unavailable_ai_analysis(
    error: str | None = None,
) -> dict[str, Any]:
    """
    Retorno padrão quando o n8n ou o Gemini não estão disponíveis.

    Essa falha não interrompe o motor de regras nem o modelo local.
    """

    return {
        "available": False,
        "provider": None,
        "comment": None,
        "error": error,
    }


def request_ai_comment(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Envia os resultados da análise para o webhook do n8n.

    O n8n é opcional. Se estiver desligado, se o Gemini falhar
    ou se a resposta for inválida, a aplicação continua funcionando.
    """

    webhook_url = os.environ.get(
        "N8N_WEBHOOK_URL",
        "",
    ).strip()

    if not webhook_url:
        return unavailable_ai_analysis(
            "Webhook do n8n não configurado."
        )

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        response_data = response.json()

        if not isinstance(response_data, dict):
            return unavailable_ai_analysis(
                "O n8n retornou um formato inválido."
            )

        comment = response_data.get(
            "comment"
        )

        if not isinstance(comment, str):
            return unavailable_ai_analysis(
                "O n8n não retornou um comentário."
            )

        comment = comment.strip()

        if not comment:
            return unavailable_ai_analysis(
                "O comentário retornado está vazio."
            )

        return {
            "available": bool(
                response_data.get(
                    "available",
                    True,
                )
            ),
            "provider": response_data.get(
                "provider",
                "Gemini",
            ),
            "comment": comment,
            "error": None,
        }

    except requests.Timeout:
        print(
            "n8n indisponível: tempo limite excedido."
        )

        return unavailable_ai_analysis(
            "Tempo limite ao consultar o n8n."
        )

    except requests.ConnectionError:
        print(
            "n8n indisponível: não foi possível estabelecer conexão."
        )

        return unavailable_ai_analysis(
            "Não foi possível conectar ao n8n."
        )

    except requests.HTTPError as error:
        print(
            "Erro HTTP retornado pelo n8n: "
            f"{error}"
        )

        return unavailable_ai_analysis(
            "O n8n retornou um erro HTTP."
        )

    except requests.RequestException as error:
        print(
            "Erro ao consultar o n8n: "
            f"{type(error).__name__}: {error}"
        )

        return unavailable_ai_analysis(
            "Falha durante a comunicação com o n8n."
        )

    except ValueError:
        print(
            "O n8n retornou uma resposta que não é JSON."
        )

        return unavailable_ai_analysis(
            "Resposta inválida retornada pelo n8n."
        )