from pathlib import Path
from typing import Any

import joblib


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "phishing_model.joblib"
VECTORIZER_PATH = PROJECT_ROOT / "models" / "vectorizer.joblib"

MODEL_NAME = "TF-IDF + Logistic Regression"

_model = None
_vectorizer = None
_load_attempted = False
_load_error = None


def load_ml_components() -> bool:
    """
    Carrega o modelo e o vetorizador apenas uma vez.

    Caso ocorra algum erro, a aplicação continua funcionando
    normalmente somente com o motor de regras.
    """

    global _model
    global _vectorizer
    global _load_attempted
    global _load_error

    if _model is not None and _vectorizer is not None:
        return True

    if _load_attempted:
        return False

    _load_attempted = True

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado: {MODEL_PATH}"
            )

        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                f"Vetorizador não encontrado: {VECTORIZER_PATH}"
            )

        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)

        if not hasattr(_model, "predict"):
            raise TypeError(
                "O arquivo carregado não possui o método predict()."
            )

        if not hasattr(_model, "predict_proba"):
            raise TypeError(
                "O arquivo carregado não possui o método predict_proba()."
            )

        if not hasattr(_vectorizer, "transform"):
            raise TypeError(
                "O vetorizador carregado não possui o método transform()."
            )

        _load_error = None

        print("Modelo de Machine Learning carregado com sucesso.")

        return True

    except Exception as error:
        _model = None
        _vectorizer = None

        _load_error = (
            f"{type(error).__name__}: {error!r}"
        )

        print(
            "Modelo de ML indisponível. "
            "A aplicação continuará somente com regras. "
            f"{_load_error}"
        )

        return False


def unavailable_result(
    error_message: str | None,
) -> dict[str, Any]:
    """
    Cria uma resposta padronizada quando o modelo
    não está disponível.
    """

    return {
        "available": False,
        "classification": None,
        "label": None,
        "phishing_probability": None,
        "legitimate_probability": None,
        "risk_score": None,
        "model": MODEL_NAME,
        "error": error_message,
    }


def classify_probability(
    phishing_probability: float,
) -> tuple[str, int | None]:
    """
    Converte a probabilidade de phishing em uma classificação.

    Faixas utilizadas:

    0% até 35%:
        Legítimo

    Acima de 35% e abaixo de 65%:
        Inconclusivo

    65% até 100%:
        Phishing
    """

    if phishing_probability >= 0.65:
        return "Phishing", 1

    if phishing_probability <= 0.35:
        return "Legítimo", 0

    return "Inconclusivo", None


def classify_email(
    email_text: str,
) -> dict[str, Any]:
    """
    Classifica um texto como phishing, legítimo ou inconclusivo.

    Retorna available=False quando o modelo estiver indisponível,
    sem interromper a aplicação Flask.
    """

    if not isinstance(email_text, str):
        email_text = str(
            email_text or ""
        )

    email_text = email_text.strip()

    if not email_text:
        return unavailable_result(
            "O texto do e-mail está vazio."
        )

    if not load_ml_components():
        return unavailable_result(
            _load_error
        )

    try:
        vectorized_text = _vectorizer.transform(
            [email_text]
        )

        probabilities = _model.predict_proba(
            vectorized_text
        )[0]

        class_indexes = {
            int(label): index
            for index, label in enumerate(
                _model.classes_
            )
        }

        if 0 not in class_indexes:
            raise ValueError(
                "A classe legítima 0 não foi encontrada no modelo."
            )

        if 1 not in class_indexes:
            raise ValueError(
                "A classe phishing 1 não foi encontrada no modelo."
            )

        legitimate_probability = float(
            probabilities[
                class_indexes[0]
            ]
        )

        phishing_probability = float(
            probabilities[
                class_indexes[1]
            ]
        )

        classification, predicted_label = (
            classify_probability(
                phishing_probability
            )
        )

        return {
            "available": True,
            "classification": classification,
            "label": predicted_label,
            "phishing_probability": round(
                phishing_probability,
                4,
            ),
            "legitimate_probability": round(
                legitimate_probability,
                4,
            ),
            "risk_score": round(
                phishing_probability * 100
            ),
            "model": MODEL_NAME,
            "error": None,
        }

    except Exception as error:
        error_message = (
            f"{type(error).__name__}: {error!r}"
        )

        print(
            "Erro ao executar o modelo. "
            "A análise continuará somente com regras. "
            f"{error_message}"
        )

        return unavailable_result(
            error_message
        )


def get_ml_status() -> dict[str, Any]:
    """
    Retorna o estado atual dos arquivos e do modelo.
    """

    available = load_ml_components()

    return {
        "available": available,
        "model_exists": MODEL_PATH.exists(),
        "vectorizer_exists": VECTORIZER_PATH.exists(),
        "model_path": str(MODEL_PATH),
        "vectorizer_path": str(VECTORIZER_PATH),
        "model": MODEL_NAME,
        "error": _load_error,
    }