from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from common import PROCESSED_DIR, exit_with_error, fail, require_package


DB_PATH = PROCESSED_DIR / "project.duckdb"
FIGURES_DIR = Path(__file__).resolve().parents[1] / "reports" / "figures"
MAIN_FAMILIES = ("Windows", "Linux", "macOS", "ChromeOS")


def save_bar(df, x_col: str, y_col: str, group_col: str, title: str, ylabel: str, path: Path) -> None:
    pivot = df.pivot(index=x_col, columns=group_col, values=y_col).fillna(0)
    ax = pivot.plot(kind="bar", figsize=(10, 5))
    ax.set_title(title)
    ax.set_xlabel("Ano")
    ax.set_ylabel(ylabel)
    ax.legend(title="Familia")
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.01, -0.22, "Fonte: Stack Overflow Developer Survey", transform=ax.transAxes, fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_line(df, x_col: str, y_col: str, group_col: str, title: str, ylabel: str, path: Path) -> None:
    pivot = df.pivot(index=x_col, columns=group_col, values=y_col).sort_index()
    ax = pivot.plot(kind="line", marker="o", figsize=(10, 5))
    ax.set_title(title)
    ax.set_xlabel("Ano")
    ax.set_ylabel(ylabel)
    ax.set_xticks(list(pivot.index))
    ax.set_xticklabels([str(int(value)) for value in pivot.index])
    ax.legend(title="Familia")
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.01,
        -0.22,
        "Fonte: Stack Overflow Developer Survey. Denominador: respondentes validos na pergunta de SO; multi-select pode somar >100%.",
        transform=ax.transAxes,
        fontsize=8,
    )
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_price_table(df, path: Path) -> None:
    display = df[["system", "edition", "open_source", "license_model", "software_price", "currency", "hardware_required"]].copy()
    display["software_price"] = display["software_price"].map(lambda value: "" if value is None else f"{value:g}")
    fig, ax = plt.subplots(figsize=(14, 0.55 * len(display) + 1.8))
    ax.axis("off")
    table = ax.table(cellText=display.values, colLabels=display.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.4)
    ax.set_title("Licenciamento e preco do software")
    ax.text(0, -0.08, "Fonte: paginas oficiais registradas em data/raw/prices/os_prices.csv", transform=ax.transAxes, fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def main() -> int:
    if not DB_PATH.exists():
        fail("Banco DuckDB ausente. Execute src/build_database.py antes.")
    duckdb = require_package("duckdb")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    stackoverflow_pct = con.execute(
        """
        WITH denom AS (
            SELECT survey_year,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS valid_respondents
            FROM survey_operating_systems
            GROUP BY survey_year
        )
        SELECT os.survey_year AS year,
               os.operating_system_family,
               count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS respondents,
               round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / denom.valid_respondents, 2) AS pct
        FROM survey_operating_systems os
        JOIN denom USING (survey_year)
        WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS')
        GROUP BY os.survey_year, os.operating_system_family, denom.valid_respondents
        ORDER BY os.survey_year, os.operating_system_family
        """
    ).df()
    save_bar(
        stackoverflow_pct,
        "year",
        "respondents",
        "operating_system_family",
        "Uso de Windows, Linux e macOS entre desenvolvedores",
        "Respondentes",
        FIGURES_DIR / "01_stackoverflow_usage_counts.png",
    )
    save_line(
        stackoverflow_pct,
        "year",
        "pct",
        "operating_system_family",
        "Evolucao percentual entre desenvolvedores",
        "% dos respondentes validos",
        FIGURES_DIR / "02_stackoverflow_usage_percent.png",
    )

    brazil = con.execute(
        """
        WITH global_denom AS (
            SELECT survey_year,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS valid_respondents
            FROM survey_operating_systems
            GROUP BY survey_year
        ),
        brazil_denom AS (
            SELECT os.survey_year,
                   count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS valid_respondents
            FROM survey_operating_systems os
            JOIN survey_respondents r USING (survey_year, respondent_id)
            WHERE r.country IN ('Brazil', 'Brasil')
            GROUP BY os.survey_year
        ),
        combined AS (
            SELECT os.survey_year AS year,
                   'Global Stack Overflow' AS sample,
                   os.operating_system_family,
                   round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / global_denom.valid_respondents, 2) AS pct
            FROM survey_operating_systems os
            JOIN global_denom USING (survey_year)
            WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS')
            GROUP BY os.survey_year, os.operating_system_family, global_denom.valid_respondents
            UNION ALL
            SELECT os.survey_year AS year,
                   'Brasil Stack Overflow (n=' || brazil_denom.valid_respondents::VARCHAR || ')' AS sample,
                   os.operating_system_family,
                   round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / brazil_denom.valid_respondents, 2) AS pct
            FROM survey_operating_systems os
            JOIN survey_respondents r USING (survey_year, respondent_id)
            JOIN brazil_denom ON brazil_denom.survey_year = os.survey_year
            WHERE r.country IN ('Brazil', 'Brasil')
              AND os.operating_system_family IN ('Windows', 'Linux', 'macOS')
            GROUP BY os.survey_year, os.operating_system_family, brazil_denom.valid_respondents
        )
        SELECT *
        FROM combined
        ORDER BY year, sample, operating_system_family
        """
    ).df()
    brazil["series"] = brazil["sample"] + " - " + brazil["operating_system_family"]
    save_line(
        brazil,
        "year",
        "pct",
        "series",
        "Brasil vs conjunto global do Stack Overflow",
        "% dos respondentes validos",
        FIGURES_DIR / "03_brazil_vs_global_stackoverflow.png",
    )

    comparison = con.execute(
        """
        WITH so_denom AS (
            SELECT survey_year,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS respondents
            FROM survey_operating_systems
            GROUP BY survey_year
        ),
        so AS (
            SELECT os.survey_year AS year,
                   'Stack Overflow Developer Survey' AS source_group,
                   os.operating_system_family,
                   round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / so_denom.respondents, 2) AS pct
            FROM survey_operating_systems os
            JOIN so_denom USING (survey_year)
            WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS', 'ChromeOS')
            GROUP BY os.survey_year, os.operating_system_family, so_denom.respondents
        ),
        sc AS (
            SELECT year(date) AS year,
                   'StatCounter desktop market share' AS source_group,
                   operating_system_family,
                   round(avg(market_share), 2) AS pct
            FROM os_market_share
            WHERE operating_system_family IN ('Windows', 'Linux', 'macOS', 'ChromeOS')
              AND year(date) BETWEEN 2022 AND 2025
            GROUP BY year(date), operating_system_family
        )
        SELECT *
        FROM so
        UNION ALL
        SELECT *
        FROM sc
        ORDER BY year, source_group, operating_system_family
        """
    ).df()
    if not comparison.empty:
        comparison["series"] = comparison["source_group"] + " - " + comparison["operating_system_family"]
        save_line(
            comparison,
            "year",
            "pct",
            "series",
            "Stack Overflow vs StatCounter desktop",
            "% por metodologia da fonte",
            FIGURES_DIR / "04_stackoverflow_vs_statcounter.png",
        )

    prices = con.execute("SELECT * FROM os_prices ORDER BY system, edition").df()
    if not prices.empty:
        prices = prices.where(prices.notna(), None)
        save_price_table(prices, FIGURES_DIR / "05_license_price_table.png")

    con.close()
    for path in sorted(FIGURES_DIR.glob("*.png")):
        print(path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
