from __future__ import annotations

import importlib
from pathlib import Path

from common import PROCESSED_DIR, PROJECT_ROOT, exit_with_error, fail, require_package
from investigate_gaming_linux import (
    SHS_CSV_URL,
    SHS_PLATFORM_CSV_URL,
    SYSTEMS,
    YEARS,
    build_main_os_map,
    build_platform_os_map,
    download_csv,
    estimate_system_share,
)


DB_PATH = PROCESSED_DIR / "project.duckdb"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def stackoverflow_linux(con) -> dict[int, float]:
    rows = con.execute(
        """
        WITH denom AS (
            SELECT survey_year,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS valid_respondents
            FROM survey_operating_systems
            GROUP BY survey_year
        )
        SELECT os.survey_year,
               count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / denom.valid_respondents AS pct
        FROM survey_operating_systems os
        JOIN denom USING (survey_year)
        WHERE os.operating_system_family = 'Linux'
        GROUP BY os.survey_year, denom.valid_respondents
        ORDER BY os.survey_year
        """
    ).fetchall()
    return {int(year): float(pct) for year, pct in rows}


def statcounter_linux(con) -> dict[int, float]:
    rows = con.execute(
        """
        SELECT year(date) AS year,
               avg(market_share) AS pct
        FROM os_market_share
        WHERE operating_system_family = 'Linux'
          AND year(date) BETWEEN 2022 AND 2025
        GROUP BY year(date)
        ORDER BY year(date)
        """
    ).fetchall()
    return {int(year): float(pct) for year, pct in rows}


def steam_linux() -> dict[int, float]:
    shs_rows, _ = download_csv(SHS_CSV_URL)
    platform_rows, _ = download_csv(SHS_PLATFORM_CSV_URL)
    main_os = build_main_os_map(shs_rows)
    platform_os = build_platform_os_map(platform_rows)
    values = {}
    for year in YEARS:
        estimate = estimate_system_share(f"{year}-12-01", "Linux", main_os, platform_os)
        values[year] = estimate.pct
    return values


def save_linux_sources_index(so: dict[int, float], statcounter: dict[int, float], steam: dict[int, float]) -> None:
    require_package("matplotlib", "matplotlib")
    plt = importlib.import_module("matplotlib.pyplot")

    series = {
        "Stack Overflow (devs)": so,
        "StatCounter (desktop)": statcounter,
        "Steam (gamers)": steam,
    }
    colors = {
        "Stack Overflow (devs)": "#2563eb",
        "StatCounter (desktop)": "#64748b",
        "Steam (gamers)": "#16a34a",
    }
    years = [2022, 2023, 2024, 2025]

    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    for label, data in series.items():
        base = data[2022]
        indexed = [data[year] * 100.0 / base for year in years]
        ax.plot(years, indexed, marker="o", linewidth=2.8, color=colors[label], label=label)
        label_offset = (-18, -18) if indexed[-1] > 240 else (-8, 9)
        ax.annotate(
            f"2025: {data[2025]:.2f}%",
            (2025, indexed[-1]),
            textcoords="offset points",
            xytext=label_offset,
            ha="right",
            fontsize=8,
        )

    ax.set_title("Linux cresceu nas tres fontes analisadas")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Indice de crescimento do Linux (2022 = 100)")
    ax.set_xticks(years)
    ax.set_xlim(2021.85, 2025.25)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper left")
    ax.text(
        0.01,
        -0.18,
        "Escalas originais sao diferentes: Stack Overflow mede respondentes; StatCounter mede market share; Steam mede usuarios da pesquisa.",
        transform=ax.transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08_linux_sources_index.png", dpi=160)
    plt.close(fig)


def save_steam_december(steam: dict[int, float]) -> None:
    require_package("matplotlib", "matplotlib")
    plt = importlib.import_module("matplotlib.pyplot")

    years = sorted(steam)
    values = [steam[year] for year in years]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, values, marker="o", linewidth=3, color="#16a34a")
    for year, value in zip(years, values):
        offset = (-4, 9) if year == max(years) else (0, 9)
        align = "right" if year == max(years) else "center"
        ax.annotate(f"{value:.2f}%", (year, value), textcoords="offset points", xytext=offset, ha=align, fontsize=9)
    ax.set_title("Steam: Linux entre usuarios da pesquisa")
    ax.set_xlabel("Dezembro de cada ano")
    ax.set_ylabel("% estimado de usuarios Steam")
    ax.set_xticks(years)
    ax.set_xlim(2021.85, 2025.25)
    ax.set_ylim(0, max(values) + 1)
    ax.grid(True, axis="y", alpha=0.25)
    ax.text(
        0.01,
        -0.18,
        "SteamOS Holo esta dentro da familia Linux. Em 2025, SteamOS Holo equivale a cerca de 0,94% do total da Steam.",
        transform=ax.transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "09_steam_linux_december.png", dpi=160)
    plt.close(fig)


def main() -> int:
    if not DB_PATH.exists():
        fail("Banco DuckDB ausente. Execute src/build_database.py antes.")

    duckdb = require_package("duckdb")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    so = stackoverflow_linux(con)
    statcounter = statcounter_linux(con)
    con.close()

    steam = steam_linux()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    save_linux_sources_index(so, statcounter, steam)
    save_steam_december(steam)

    for path in (FIGURES_DIR / "08_linux_sources_index.png", FIGURES_DIR / "09_steam_linux_december.png"):
        print(path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
