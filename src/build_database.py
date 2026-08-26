from __future__ import annotations

import csv
from pathlib import Path

from common import (
    PROCESSED_DIR,
    RAW_PRICES_DIR,
    RAW_STATCOUNTER_DIR,
    ensure_directories,
    exit_with_error,
    fail,
    log,
    require_package,
)


DB_PATH = PROCESSED_DIR / "project.duckdb"
RESPONDENTS_PARQUET = PROCESSED_DIR / "stackoverflow" / "year=*" / "survey_respondents.parquet"
SYSTEMS_PARQUET = PROCESSED_DIR / "stackoverflow" / "year=*" / "survey_operating_systems.parquet"
PRICES_CSV = RAW_PRICES_DIR / "os_prices.csv"
STATCOUNTER_CSV = RAW_STATCOUNTER_DIR / "os_market_share.csv"

PRICE_COLUMNS = [
    "collected_at",
    "system",
    "edition",
    "license_model",
    "open_source",
    "software_price",
    "currency",
    "hardware_required",
    "support_model",
    "source",
    "notes",
]

STATCOUNTER_COLUMNS = [
    "date",
    "region",
    "operating_system_original",
    "operating_system_family",
    "market_share",
    "source",
    "collected_at",
]


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def ensure_csv_with_header(path: Path, columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(columns)


def validate_csv_header(path: Path, columns: list[str]) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        try:
            header = next(csv.reader(handle))
        except StopIteration:
            return False
    missing = [column for column in columns if column not in header]
    if missing:
        fail(f"CSV {path} nao contem colunas obrigatorias: {missing}")
    return True


def parquet_files_exist() -> bool:
    root = PROCESSED_DIR / "stackoverflow"
    return root.exists() and any(root.glob("year=*/survey_respondents.parquet")) and any(
        root.glob("year=*/survey_operating_systems.parquet")
    )


def main() -> int:
    ensure_directories()
    duckdb = require_package("duckdb")
    ensure_csv_with_header(PRICES_CSV, PRICE_COLUMNS)
    ensure_csv_with_header(STATCOUNTER_CSV, STATCOUNTER_COLUMNS)

    if not parquet_files_exist():
        fail("Parquet processado ausente. Execute src/transform_stackoverflow.py antes.")

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    respondents_glob = quote_literal(str(RESPONDENTS_PARQUET))
    systems_glob = quote_literal(str(SYSTEMS_PARQUET))

    log("Criando tabelas Stack Overflow no DuckDB")
    con.execute(
        f"""
        CREATE TABLE survey_respondents AS
        SELECT *
        FROM read_parquet({respondents_glob})
        WHERE respondent_id IS NOT NULL
        """
    )
    con.execute(
        f"""
        CREATE TABLE survey_operating_systems AS
        SELECT survey_year, respondent_id, operating_system_original,
               operating_system_normalized, operating_system_family
        FROM read_parquet({systems_glob})
        WHERE operating_system_normalized IS NOT NULL
        """
    )

    validate_csv_header(PRICES_CSV, PRICE_COLUMNS)
    validate_csv_header(STATCOUNTER_CSV, STATCOUNTER_COLUMNS)

    log("Criando tabelas opcionais de StatCounter e precos")
    con.execute(
        f"""
        CREATE TABLE os_prices AS
        SELECT collected_at::DATE AS collected_at,
               system,
               edition,
               license_model,
               open_source,
               try_cast(software_price AS DOUBLE) AS software_price,
               currency,
               hardware_required,
               support_model,
               source,
               notes
        FROM read_csv_auto({quote_literal(str(PRICES_CSV))}, header=true, all_varchar=true)
        """
    )
    con.execute(
        f"""
        CREATE TABLE os_market_share AS
        SELECT date::DATE AS date,
               region,
               operating_system_original,
               operating_system_family,
               try_cast(market_share AS DOUBLE) AS market_share,
               source,
               collected_at::DATE AS collected_at
        FROM read_csv_auto({quote_literal(str(STATCOUNTER_CSV))}, header=true, all_varchar=true)
        """
    )

    tables = con.execute("SHOW TABLES").fetchall()
    for (table,) in tables:
        count = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count:,} linhas".replace(",", "."))
    con.close()
    print(f"DuckDB criado em: {DB_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
