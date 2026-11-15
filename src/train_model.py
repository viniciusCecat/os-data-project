from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from common import PROCESSED_DIR, PROJECT_ROOT, exit_with_error, fail, require_package


DB_PATH = PROCESSED_DIR / "project.duckdb"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_evaluation.md"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
MISSINGNESS_FIGURE = FIGURES_DIR / "10_model_missingness.png"
CONFUSION_FIGURE = FIGURES_DIR / "11_model_confusion_matrix.png"
FEATURE_COLUMNS = (
    "country",
    "age",
    "employment",
    "developer_type",
)
TARGET_COLUMN = "uses_linux"
YEAR_COLUMN = "survey_year"


def load_model_data(con) -> pd.DataFrame:
    return con.execute(
        """
        WITH os_by_respondent AS (
            SELECT survey_year,
                   respondent_id,
                   max(CASE WHEN operating_system_family = 'Linux' THEN 1 ELSE 0 END) AS uses_linux
            FROM survey_operating_systems
            GROUP BY survey_year, respondent_id
        )
        SELECT r.survey_year,
               r.country,
               r.age,
               r.employment,
               r.developer_type,
               r.professional_experience,
               os.uses_linux
        FROM survey_respondents r
        JOIN os_by_respondent os USING (survey_year, respondent_id)
        ORDER BY r.survey_year, r.respondent_id
        """
    ).df()


def make_classifier(features: list[str], estimator) -> Pipeline:
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Nao informado")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        [("categorical", categorical_pipeline, features)],
        remainder="drop",
    )
    return Pipeline(
        [
            ("preprocessing", preprocessing),
            ("classifier", estimator),
        ]
    )


def metric_row(name: str, y_true, y_pred, y_score) -> dict[str, float | str | None]:
    return {
        "model": name,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision_linux": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_linux": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_linux": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_score)) if len(set(y_true)) == 2 else None,
    }


def evaluate_dataset(data: pd.DataFrame) -> dict:
    required = {YEAR_COLUMN, TARGET_COLUMN, *FEATURE_COLUMNS}
    missing_columns = required - set(data.columns)
    if missing_columns:
        fail(f"Colunas necessarias para modelagem ausentes: {sorted(missing_columns)}")

    data = data.dropna(subset=[YEAR_COLUMN, TARGET_COLUMN]).copy()
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)
    years = sorted(data[YEAR_COLUMN].unique())
    if len(years) < 2:
        fail("A avaliacao temporal exige dados de pelo menos dois anos.")

    test_year = years[-1]
    train = data[data[YEAR_COLUMN] < test_year]
    test = data[data[YEAR_COLUMN] == test_year]
    if train.empty or test.empty:
        fail("Nao foi possivel separar os anos de treino e teste.")
    if train[TARGET_COLUMN].nunique() < 2:
        fail("O conjunto de treino precisa conter as duas classes do alvo Linux.")

    features = list(FEATURE_COLUMNS)
    x_train, y_train = train[features], train[TARGET_COLUMN]
    x_test, y_test = test[features], test[TARGET_COLUMN]

    models = {
        "Baseline (classe majoritaria)": DummyClassifier(strategy="most_frequent"),
        "Regressao logistica": make_classifier(
            features,
            LogisticRegression(max_iter=1000, random_state=42),
        ),
        "Arvore de decisao": make_classifier(
            features,
            DecisionTreeClassifier(
                max_depth=12,
                min_samples_leaf=100,
                random_state=42,
            ),
        ),
    }
    results = []
    fitted_models = {}
    predictions = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        if hasattr(model, "predict_proba"):
            y_score = model.predict_proba(x_test)[:, 1]
        else:
            y_score = y_pred
        results.append(metric_row(name, y_test, y_pred, y_score))
        fitted_models[name] = model
        predictions[name] = y_pred

    chosen = max(
        results,
        key=lambda row: (
            row["f1_linux"],
            row["balanced_accuracy"],
            row["roc_auc"] if row["roc_auc"] is not None else -1,
        ),
    )
    return {
        "data": data,
        "features": features,
        "train": train,
        "test": test,
        "test_year": test_year,
        "results": results,
        "chosen": chosen,
        "models": fitted_models,
        "predictions": predictions,
        "y_test": y_test,
    }


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def write_missingness_figure(data: pd.DataFrame) -> None:
    missing = (
        data[list(FEATURE_COLUMNS)]
        .isna()
        .mean()
        .sort_values(ascending=True)
        .rename("missing_pct")
        .mul(100)
        .rename_axis("feature")
        .reset_index()
    )
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=missing, x="missing_pct", y="feature", color="#3b82f6", ax=ax)
    ax.set_title("Valores ausentes nas variaveis preditoras")
    ax.set_xlabel("% de respondentes sem resposta")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(MISSINGNESS_FIGURE, dpi=160)
    plt.close(fig)


def write_confusion_figure(result: dict) -> None:
    chosen_name = result["chosen"]["model"]
    predicted = result["predictions"][chosen_name]
    matrix = confusion_matrix(result["y_test"], predicted, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Nao Linux", "Linux"],
        yticklabels=["Nao Linux", "Linux"],
        ax=ax,
    )
    ax.set_title(f"Matriz de confusao: {chosen_name}")
    ax.set_xlabel("Classe prevista")
    ax.set_ylabel("Classe real")
    fig.tight_layout()
    fig.savefig(CONFUSION_FIGURE, dpi=160)
    plt.close(fig)


def write_report(result: dict, missing_respondents: int) -> None:
    data = result["data"]
    features = result["features"]
    train = result["train"]
    test = result["test"]
    missingness = data[features].isna().sum()
    metrics = [
        "| Modelo | Acuracia | Acuracia balanceada | Precisao Linux | Recall Linux | F1 Linux | ROC-AUC |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["results"]:
        roc_auc = "NA" if row["roc_auc"] is None else percent(row["roc_auc"])
        metrics.append(
            f"| {row['model']} | {percent(row['accuracy'])} | "
            f"{percent(row['balanced_accuracy'])} | {percent(row['precision_linux'])} | "
            f"{percent(row['recall_linux'])} | {percent(row['f1_linux'])} | {roc_auc} |"
        )

    missing_table = [
        "| Variavel | Ausentes | Percentual |",
        "| --- | ---: | ---: |",
    ]
    for column, count in missingness.items():
        missing_table.append(f"| {column} | {int(count)} | {percent(count / len(data))} |")

    train_distribution = train[TARGET_COLUMN].value_counts(normalize=True).sort_index()
    test_distribution = test[TARGET_COLUMN].value_counts(normalize=True).sort_index()
    chosen = result["chosen"]
    lines = [
        "# Avaliacao do modelo de classificacao",
        "",
        "## Pergunta de modelagem",
        "",
        "E possivel classificar se um respondente selecionou Linux a partir de suas respostas de perfil no survey?",
        "O modelo identifica associacoes preditivas e nao estima efeito causal.",
        "",
        "## Preparacao e desenho da avaliacao",
        "",
        "- Cada observacao e um respondente com ao menos uma resposta valida de sistema operacional.",
        "- O alvo e binario: Linux (1) se qualquer resposta normalizada pertence a familia Linux; caso contrario, nao Linux (0).",
        f"- Respondentes sem resposta valida de sistema operacional excluidos: {missing_respondents}.",
        f"- Variaveis preditoras: {', '.join(features)}.",
        "- Experiencia profissional foi excluida porque a coluna mudou de `YearsCodePro` para `WorkExp` em 2025 e nao e diretamente comparavel entre treino e teste.",
        "- Nulos nas variaveis preditoras sao imputados como categoria `Nao informado` e categorias sao codificadas com one-hot encoding.",
        f"- Treino: anos anteriores a {result['test_year']} ({len(train)} respondentes).",
        f"- Teste temporal: {result['test_year']} ({len(test)} respondentes), mantido fora do treino.",
        "- O ano nao e usado como preditor. A divisao temporal testa generalizacao para um survey posterior.",
        "",
        "## Dados ausentes",
        "",
        *missing_table,
        "",
        "![Percentual de valores ausentes por variavel](figures/10_model_missingness.png)",
        "",
        "## Balanceamento do alvo",
        "",
        f"- Treino — nao Linux: {percent(float(train_distribution.get(0, 0)))}; Linux: {percent(float(train_distribution.get(1, 0)))}.",
        f"- Teste — nao Linux: {percent(float(test_distribution.get(0, 0)))}; Linux: {percent(float(test_distribution.get(1, 0)))}.",
        "- Nao foi aplicado reamostragem ou peso de classe: a distribuicao deve ser julgada pelos percentuais reportados, e as metricas incluem acuracia balanceada, precisao e recall.",
        "",
        "## Modelos e metricas",
        "",
        "A classe majoritaria e usada como baseline. Regressao logistica e arvore de decisao sao comparadas sobre a mesma codificacao one-hot; a arvore limita profundidade e tamanho minimo das folhas para reduzir sobreajuste. A selecao entre classificadores usa F1 para a classe Linux, com acuracia balanceada e ROC-AUC como desempate.",
        "",
        *metrics,
        "",
        f"Modelo selecionado: **{chosen['model']}** (F1 Linux = {percent(chosen['f1_linux'])}).",
        "",
        "![Matriz de confusao do modelo selecionado](figures/11_model_confusion_matrix.png)",
        "",
        "## Interpretacao e limitacoes",
        "",
        f"No teste temporal, o modelo selecionado obteve acuracia balanceada de {percent(chosen['balanced_accuracy'])} e ROC-AUC de {'NA' if chosen['roc_auc'] is None else percent(chosen['roc_auc'])}. Esse desempenho indica sinal preditivo limitado/modesto, e deve ser comparado com a prevalencia da classe, nao apresentado como previsao de alta confiabilidade.",
        "",
        "Os resultados descrevem capacidade preditiva para respondentes do survey e nao demonstram que perfil profissional ou demografico cause uso de Linux. Os surveys nao acompanham a mesma pessoa entre anos, e mudancas de schema, amostragem e contexto podem reduzir a generalizacao para outros anos ou populacoes.",
        "",
        "Relatorio gerado por `python src/train_model.py` a partir do DuckDB local.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not DB_PATH.exists():
        fail("Banco DuckDB ausente. Execute src/build_database.py antes.")
    duckdb = require_package("duckdb")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        total_respondents = con.execute("SELECT count(*) FROM survey_respondents").fetchone()[0]
        data = load_model_data(con)
    finally:
        con.close()

    result = evaluate_dataset(data)
    missing_respondents = total_respondents - len(data)
    write_missingness_figure(data)
    write_confusion_figure(result)
    write_report(result, missing_respondents)
    print(f"Relatorio de modelagem: {REPORT_PATH}")
    for row in result["results"]:
        print(
            f"{row['model']}: F1 Linux={percent(row['f1_linux'])}, "
            f"acuracia balanceada={percent(row['balanced_accuracy'])}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
