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


def save_brazil_comparison(df, path: Path) -> None:
    systems = ("Linux", "Windows", "macOS")
    colors = {"Linux": "#16a34a", "Windows": "#2563eb", "macOS": "#9333ea"}

    fig, (trend_ax, bars_ax) = plt.subplots(
        1,
        2,
        figsize=(13.2, 5.1),
        gridspec_kw={"width_ratios": [1.15, 1]},
    )

    linux_df = df[df["operating_system_family"] == "Linux"]
    for sample, style, marker in (("Brasil", "-", "o"), ("Global", "--", "s")):
        sample_df = linux_df[linux_df["sample"] == sample].sort_values("year")
        trend_ax.plot(
            sample_df["year"],
            sample_df["pct"],
            marker=marker,
            linestyle=style,
            linewidth=2.6,
            color=colors["Linux"],
            label=sample,
        )
        for _, row in sample_df.iterrows():
            trend_ax.annotate(
                f"{row['pct']:.1f}%",
                (row["year"], row["pct"]),
                textcoords="offset points",
                xytext=(0, 9 if sample == "Brasil" else -16),
                ha="center",
                fontsize=9,
                bbox={"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "none", "alpha": 0.8},
            )
    trend_ax.set_title("Linux no Stack Overflow")
    trend_ax.set_xlabel("Ano")
    trend_ax.set_ylabel("% dos respondentes validos")
    trend_ax.set_xticks(sorted(linux_df["year"].unique()))
    trend_ax.set_ylim(40, 58)
    trend_ax.grid(True, axis="y", alpha=0.25)
    trend_ax.legend(title="Amostra", loc="lower right")

    latest = df[df["year"] == 2025].copy()
    y_positions = list(range(len(systems)))
    bar_height = 0.34
    for offset, sample, color in ((-bar_height / 2, "Global", "#94a3b8"), (bar_height / 2, "Brasil", "#159447")):
        values = []
        for system in systems:
            row = latest[(latest["sample"] == sample) & (latest["operating_system_family"] == system)]
            values.append(float(row["pct"].iloc[0]))
        bars = bars_ax.barh(
            [position + offset for position in y_positions],
            values,
            height=bar_height,
            color=color,
            label=sample,
        )
        for bar, value in zip(bars, values):
            label_color = "white" if value >= 20 else "#17202a"
            label_x = max(value - 1.2, value + 0.8) if value < 20 else value - 1.2
            label_ha = "left" if value < 20 else "right"
            bars_ax.text(
                label_x,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}%",
                va="center",
                ha=label_ha,
                fontsize=9,
                fontweight="bold",
                color=label_color,
            )
    bars_ax.set_title("2025 por sistema")
    bars_ax.set_yticks(y_positions)
    bars_ax.set_yticklabels(systems)
    bars_ax.set_xlabel("% dos respondentes validos")
    bars_ax.set_xlim(0, 64)
    bars_ax.grid(True, axis="x", alpha=0.2)
    bars_ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.03), ncol=2, frameon=False)

    brazil_n = (
        df[df["sample"] == "Brasil"][["year", "sample_n"]]
        .drop_duplicates()
        .sort_values("year")
    )
    sample_text = ", ".join(f"{int(row.year)} n={int(row.sample_n)}" for row in brazil_n.itertuples())
    fig.suptitle("Brasil vs conjunto global do Stack Overflow")
    fig.text(
        0.01,
        0.01,
        f"Fonte: Stack Overflow Developer Survey. Brasil e recorte por Country. Amostra Brasil por ano: {sample_text}. "
        "Multi-select pode somar >100%.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    fig.savefig(path, dpi=160)
    plt.close(fig)


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
                   'Global' AS sample,
                   os.operating_system_family,
                   global_denom.valid_respondents AS sample_n,
                   round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / global_denom.valid_respondents, 2) AS pct
            FROM survey_operating_systems os
            JOIN global_denom USING (survey_year)
            WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS')
            GROUP BY os.survey_year, os.operating_system_family, global_denom.valid_respondents
            UNION ALL
            SELECT os.survey_year AS year,
                   'Brasil' AS sample,
                   os.operating_system_family,
                   brazil_denom.valid_respondents AS sample_n,
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
    save_brazil_comparison(brazil, FIGURES_DIR / "03_brazil_vs_global_stackoverflow.png")

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
