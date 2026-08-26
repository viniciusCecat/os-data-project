from __future__ import annotations

from common import YEARS, exit_with_error, fail, log, read_csv_header, require_package, stackoverflow_results_path
from schema_mapping import infer_mapping, possible_fields


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def inspect_year(con, year: int) -> None:
    path = stackoverflow_results_path(year)
    header = read_csv_header(path)
    path_sql = quote_literal(str(path))
    relation = f"read_csv_auto({path_sql}, header=true, sample_size=20000, ignore_errors=false)"
    row_count = con.execute(f"SELECT count(*) FROM {relation}").fetchone()[0]
    types = con.execute(f"DESCRIBE SELECT * FROM {relation}").fetchall()

    null_exprs = [
        (
            f"sum(CASE WHEN {quote_identifier(column)} IS NULL "
            f"OR trim(CAST({quote_identifier(column)} AS VARCHAR)) = '' THEN 1 ELSE 0 END) "
            f"AS {quote_identifier(column)}"
        )
        for column in header
    ]
    null_counts = con.execute(f"SELECT {', '.join(null_exprs)} FROM {relation}").fetchone()
    mapping = infer_mapping(header)
    candidates = possible_fields(header)

    print(f"\n=== {year} ===")
    print(f"[INFO] {row_count:,} linhas encontradas".replace(",", "."))
    print(f"[INFO] {len(header)} colunas encontradas")
    print("Colunas:")
    for column in header:
        print(f"- {column}")
    print("Tipos inferidos:")
    for name, dtype, *_ in types:
        print(f"- {name}: {dtype}")
    print("Percentual de valores nulos:")
    for column, null_count in zip(header, null_counts, strict=True):
        pct = (null_count / row_count * 100) if row_count else 0
        print(f"- {column}: {pct:.2f}%")
    print("Mapeamento inferido:")
    for field, value in mapping.__dict__.items():
        print(f"- {field}: {value or 'NAO IDENTIFICADO'}")
    print("Campos possivelmente relacionados:")
    for label, values in candidates.items():
        print(f"- {label}: {', '.join(values) if values else 'nenhum'}")


def main() -> int:
    duckdb = require_package("duckdb")
    con = duckdb.connect(":memory:")
    missing = [str(stackoverflow_results_path(year)) for year in YEARS if not stackoverflow_results_path(year).exists()]
    if missing:
        fail("Arquivos brutos ausentes. Execute src/download_stackoverflow.py antes.\n" + "\n".join(missing))
    for year in YEARS:
        log(f"Inspecionando survey {year}")
        inspect_year(con, year)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
