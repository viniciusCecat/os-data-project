from __future__ import annotations

from common import (
    PROCESSED_DIR,
    RAW_PRICES_DIR,
    RAW_STACKOVERFLOW_DIR,
    RAW_STATCOUNTER_DIR,
    YEARS,
    exit_with_error,
    format_size,
    is_git_lfs_pointer,
    sha256_file,
    stackoverflow_results_path,
)


DB_PATH = PROCESSED_DIR / "project.duckdb"
STATCOUNTER_CSV = RAW_STATCOUNTER_DIR / "os_market_share.csv"
PRICES_CSV = RAW_PRICES_DIR / "os_prices.csv"


def print_problem(problems: list[str], message: str) -> None:
    problems.append(message)
    print(f"- {message}")


def raw_report(problems: list[str]) -> int:
    total = 0
    print("\nStack Overflow")
    for year in YEARS:
        path = stackoverflow_results_path(year)
        if not path.exists():
            print(f"{year}: AUSENTE")
            print_problem(problems, f"Arquivo bruto ausente para {year}: {path}")
            continue
        if is_git_lfs_pointer(path):
            print(f"{year}: POINTER LFS")
            print_problem(problems, f"Arquivo bruto ainda e ponteiro Git LFS para {year}")
            continue
        size = path.stat().st_size
        total += size
        print(f"{year}: OK | {format_size(size)} | sha256: {sha256_file(path)}")
    return total


def parquet_report(problems: list[str]) -> None:
    print("\nParquet")
    for year in YEARS:
        base = PROCESSED_DIR / "stackoverflow" / f"year={year}"
        respondents = base / "survey_respondents.parquet"
        systems = base / "survey_operating_systems.parquet"
        if respondents.exists() and systems.exists():
            size = respondents.stat().st_size + systems.stat().st_size
            print(f"{year}: OK | {format_size(size)}")
        else:
            print(f"{year}: AUSENTE")
            print_problem(problems, f"Parquet ausente para {year}")


def duckdb_report(problems: list[str]) -> None:
    print("\nDuckDB")
    if not DB_PATH.exists():
        print("AUSENTE")
        print_problem(problems, "Banco DuckDB ausente. Execute src/build_database.py.")
        return
    try:
        import duckdb
    except ImportError:
        print("NAO VALIDADO")
        print_problem(problems, "Pacote duckdb nao instalado.")
        return

    con = duckdb.connect(str(DB_PATH), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    required = {"survey_respondents", "survey_operating_systems", "os_market_share", "os_prices"}
    missing = required - tables
    if missing:
        print_problem(problems, f"Tabelas ausentes no DuckDB: {sorted(missing)}")
    print("OK" if not missing else "INCOMPLETO")

    if "survey_respondents" in tables:
        print("\nRespondentes")
        rows = con.execute(
            """
            SELECT survey_year, count(*)
            FROM survey_respondents
            GROUP BY survey_year
            ORDER BY survey_year
            """
        ).fetchall()
        for year, count in rows:
            print(f"{year}: {count:,}".replace(",", "."))

    if "survey_operating_systems" in tables:
        print("\nOS encontrados")
        rows = con.execute(
            """
            SELECT operating_system_family, count(*) AS n
            FROM survey_operating_systems
            GROUP BY operating_system_family
            ORDER BY n DESC, operating_system_family
            """
        ).fetchall()
        for family, count in rows:
            print(f"{family}: {count:,}".replace(",", "."))

    if "os_market_share" in tables:
        print("\nStatCounter")
        rows = con.execute(
            """
            SELECT min(date), max(date), count(*), count(DISTINCT operating_system_original)
            FROM os_market_share
            """
        ).fetchone()
        print(f"Periodo: {rows[0]} a {rows[1]} | linhas: {rows[2]} | sistemas originais: {rows[3]}")
        bad_rows = con.execute(
            """
            SELECT count(*)
            FROM os_market_share
            WHERE date IS NULL
               OR collected_at IS NULL
               OR market_share IS NULL
               OR market_share < 0
               OR market_share > 100
               OR source IS NULL
               OR trim(source) = ''
            """
        ).fetchone()[0]
        if bad_rows:
            print_problem(problems, f"StatCounter contem {bad_rows} linha(s) invalida(s).")
        monthly_totals = con.execute(
            """
            SELECT count(*)
            FROM (
                SELECT date, region, sum(market_share) AS total
                FROM os_market_share
                GROUP BY date, region
                HAVING total < 95 OR total > 101
            )
            """
        ).fetchone()[0]
        if monthly_totals:
            print_problem(problems, f"StatCounter contem {monthly_totals} mes(es) fora da tolerancia de soma.")

    if "os_prices" in tables:
        print("\nPrecos")
        rows = con.execute(
            """
            SELECT count(*), count(DISTINCT system)
            FROM os_prices
            """
        ).fetchone()
        print(f"Linhas: {rows[0]} | sistemas: {rows[1]}")
        bad_rows = con.execute(
            """
            SELECT count(*)
            FROM os_prices
            WHERE collected_at IS NULL
               OR system IS NULL
               OR trim(system) = ''
               OR software_price IS NULL
               OR software_price < 0
               OR currency NOT IN ('USD')
               OR hardware_required IS NULL
               OR trim(hardware_required) = ''
               OR source IS NULL
               OR trim(source) = ''
            """
        ).fetchone()[0]
        if bad_rows:
            print_problem(problems, f"os_prices contem {bad_rows} linha(s) invalida(s).")
    con.close()


def raw_complementary_report(problems: list[str]) -> None:
    print("\nFontes complementares")
    if STATCOUNTER_CSV.exists():
        print(f"StatCounter CSV: OK | {format_size(STATCOUNTER_CSV.stat().st_size)}")
    else:
        print_problem(problems, f"StatCounter CSV ausente: {STATCOUNTER_CSV}")
    if PRICES_CSV.exists():
        print(f"Precos CSV: OK | {format_size(PRICES_CSV.stat().st_size)}")
    else:
        print_problem(problems, f"Precos CSV ausente: {PRICES_CSV}")


def main() -> int:
    problems: list[str] = []
    print("=== DATASET VALIDATION ===")
    raw_size = raw_report(problems)
    print(f"\nArquivos brutos: {len(list(RAW_STACKOVERFLOW_DIR.glob('year=*/results.csv')))}")
    print(f"Tamanho bruto: {format_size(raw_size)}")
    raw_complementary_report(problems)
    parquet_report(problems)
    duckdb_report(problems)

    print("\nProblemas encontrados:")
    print(len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
