from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.ml_classifier import safe_predict_phishing


def main() -> None:
    examples = [
        """
        URGENTE: sua conta será bloqueada.

        Confirme imediatamente sua senha e seus dados bancários
        acessando o link enviado nesta mensagem.
        """,
        """
        Olá,

        A aula de amanhã ocorrerá normalmente às 14 horas.
        O material está disponível na plataforma da disciplina.

        Atenciosamente,
        Professor
        """,
    ]

    for position, email_text in enumerate(examples, start=1):
        result = safe_predict_phishing(email_text)

        print(f"\nExemplo {position}")
        print(result)


if __name__ == "__main__":
    main()