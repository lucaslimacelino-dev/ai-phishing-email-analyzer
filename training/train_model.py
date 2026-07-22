from pathlib import Path

import joblib
import pandas as pd
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIRECTORY = PROJECT_ROOT / "models"

MODEL_PATH = MODELS_DIRECTORY / "phishing_model.joblib"
VECTORIZER_PATH = MODELS_DIRECTORY / "vectorizer.joblib"

DATASET_NAME = "ealvaradob/phishing-dataset"
DATASET_CONFIGURATION = "texts"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_phishing_dataset() -> pd.DataFrame:
    """
    Baixa diretamente o arquivo texts.json do Hugging Face,
    sem executar o script antigo do dataset.
    """

    print("Baixando o dataset textual do Hugging Face...")

    dataset_url = (
        "https://huggingface.co/datasets/"
        "ealvaradob/phishing-dataset/resolve/main/texts.json"
    )

    dataset = load_dataset(
        "json",
        data_files={
            "train": dataset_url,
        },
    )

    dataframe = dataset["train"].to_pandas()

    required_columns = {"text", "label"}

    if not required_columns.issubset(dataframe.columns):
        raise ValueError(
            "O dataset precisa possuir as colunas 'text' e 'label'. "
            f"Colunas encontradas: {dataframe.columns.tolist()}"
        )

    dataframe = dataframe[["text", "label"]].copy()

    dataframe["text"] = (
        dataframe["text"]
        .astype(str)
        .str.strip()
    )

    dataframe["label"] = pd.to_numeric(
        dataframe["label"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=["text", "label"],
    )

    dataframe = dataframe[
        dataframe["text"] != ""
    ]

    dataframe = dataframe[
        dataframe["label"].isin([0, 1])
    ]

    dataframe["label"] = dataframe["label"].astype(int)

    dataframe = dataframe.drop_duplicates(
        subset=["text"],
    )

    dataframe = dataframe.reset_index(drop=True)

    print("Dataset carregado com sucesso.")

    return dataframe

def display_dataset_information(dataframe: pd.DataFrame) -> None:
    print("\nInformações do dataset")
    print("-" * 45)

    print(f"Quantidade total: {len(dataframe)}")

    print("\nDistribuição das classes:")
    print(dataframe["label"].value_counts().sort_index())

    print("\nPercentuais:")
    percentages = (
        dataframe["label"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
    )

    print(percentages)

    print("\nSignificado das classes:")
    print("0 = Benigno")
    print("1 = Phishing")


def split_dataset(dataframe: pd.DataFrame):
    x = dataframe["text"]
    y = dataframe["label"]

    return train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def create_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    max_features=100000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    solver="liblinear",
                ),
            ),
        ]
    )


def evaluate_model(
    model: Pipeline,
    x_test: pd.Series,
    y_test: pd.Series,
) -> None:
    predictions = model.predict(x_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print("\nResultado da avaliação")
    print("-" * 45)
    print(f"Acurácia: {accuracy:.4f}")

    print("\nMatriz de confusão:")
    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )

    print("\nRelatório de classificação:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Benigno",
                "Phishing",
            ],
            digits=4,
            zero_division=0,
        )
    )


def save_model(model: Pipeline) -> None:
    MODELS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    classifier = model.named_steps["classifier"]
    vectorizer = model.named_steps["vectorizer"]

    joblib.dump(
        classifier,
        MODEL_PATH,
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH,
    )

    print("\nArquivos salvos:")
    print(f"Modelo: {MODEL_PATH}")
    print(f"Vetorizador: {VECTORIZER_PATH}")


def main() -> None:
    dataframe = load_phishing_dataset()

    display_dataset_information(dataframe)

    x_train, x_test, y_train, y_test = split_dataset(
        dataframe,
    )

    print("\nDivisão dos dados")
    print("-" * 45)
    print(f"Treinamento: {len(x_train)}")
    print(f"Teste: {len(x_test)}")

    model = create_pipeline()

    print("\nTreinando TF-IDF + Regressão Logística...")

    model.fit(
        x_train,
        y_train,
    )

    evaluate_model(
        model,
        x_test,
        y_test,
    )

    save_model(model)

    print("\nTreinamento concluído com sucesso.")


if __name__ == "__main__":
    main()