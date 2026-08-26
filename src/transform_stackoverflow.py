from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Iterable

from common import (
    DOCS_DIR,
    PROCESSED_DIR,
    PipelineError,
    YEARS,
    ensure_directories,
    exit_with_error,
    fail,
    format_size,
    log,
    raise_csv_field_size_limit,
    read_csv_header,
    stackoverflow_results_path,
)
from normalize_os import normalize_os
from schema_mapping import FieldMapping, infer_mapping


BATCH_SIZE = 20_000


def optional_value(row: dict[str, str], column: str | None) -> str | None:
    if not column:
        return None
    value = row.get(column)
    if value is None:
        return None
    text = str(value).strip()
    if text.casefold() in {"", "na", "n/a", "nan", "none", "null"}:
        return None
    return text


def get_required_mapping(year: int, header: list[str]) -> FieldMapping:
    mapping = infer_mapping(header)
    if not mapping.respondent_id:
        fail(f"Coluna de identificador nao identificada no survey {year}. Colunas reais: {header}")
    if not mapping.operating_system:
        fail(f"Coluna de sistema operacional nao identificada no survey {year}. Colunas reais: {header}")
    return mapping


def write_batches(records: Iterable[dict], output_path: Path, schema) -> int:
    pa = __import__("pyarrow")
    pq = __import__("pyarrow.parquet").parquet
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    count = 0
    batch: list[dict] = []
    try:
        for record in records:
            batch.append(record)
            if len(batch) >= BATCH_SIZE:
                table = pa.Table.from_pylist(batch, schema=schema)
                writer = writer or pq.ParquetWriter(output_path, schema, compression="zstd")
                writer.write_table(table)
                count += len(batch)
                batch.clear()
        if batch:
            table = pa.Table.from_pylist(batch, schema=schema)
            writer = writer or pq.ParquetWriter(output_path, schema, compression="zstd")
            writer.write_table(table)
            count += len(batch)
    finally:
        if writer:
            writer.close()
    if count == 0:
        table = pa.Table.from_pylist([], schema=schema)
        pq.write_table(table, output_path, compression="zstd")
    return count


def row_records(csv_path: Path, year: int, mapping: FieldMapping):
    with csv_path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.DictReader(handle)
        seen_ids: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            respondent_id = optional_value(row, mapping.respondent_id)
            if respondent_id is None:
                fail(f"Identificador nulo no survey {year}, linha CSV {row_number}.")
            key = f"{year}:{respondent_id}"
            if key in seen_ids:
                fail(f"Identificador duplicado dentro do survey {year}: {respondent_id}")
            seen_ids.add(key)
            yield {
                "survey_year": year,
                "respondent_id": str(respondent_id),
                "country": optional_value(row, mapping.country),
                "age": optional_value(row, mapping.age),
                "employment": optional_value(row, mapping.employment),
                "developer_type": optional_value(row, mapping.developer_type),
                "professional_experience": optional_value(row, mapping.professional_experience),
            }


def os_records(csv_path: Path, year: int, mapping: FieldMapping):
    with csv_path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            respondent_id = optional_value(row, mapping.respondent_id)
            if respondent_id is None:
                fail(f"Identificador nulo no survey {year}, linha CSV {row_number}.")
            os_value = optional_value(row, mapping.operating_system)
            for normalized in normalize_os(os_value):
                yield {
                    "survey_year": year,
                    "respondent_id": str(respondent_id),
                    "operating_system_original": normalized.operating_system_original,
                    "operating_system_normalized": normalized.operating_system_normalized,
                    "operating_system_family": normalized.operating_system_family,
                }


def pyarrow_schema():
    pa = __import__("pyarrow")
    respondent_schema = pa.schema(
        [
            ("survey_year", pa.int16()),
            ("respondent_id", pa.string()),
            ("country", pa.string()),
            ("age", pa.string()),
            ("employment", pa.string()),
            ("developer_type", pa.string()),
            ("professional_experience", pa.string()),
        ]
    )
    os_schema = pa.schema(
        [
            ("survey_year", pa.int16()),
            ("respondent_id", pa.string()),
            ("operating_system_original", pa.string()),
            ("operating_system_normalized", pa.string()),
            ("operating_system_family", pa.string()),
        ]
    )
    return respondent_schema, os_schema


def write_schema_mapping(mapping_by_year: dict[int, FieldMapping]) -> None:
    lines = [
        "# Schema mapping",
        "",
        "Gerado a partir dos cabecalhos reais dos CSVs em `data/raw/stackoverflow/`.",
        "",
        "Ano | Campo original | Campo padronizado",
        "--- | --- | ---",
    ]
    for year, mapping in mapping_by_year.items():
        for standardized, original in mapping.__dict__.items():
            lines.append(f"{year} | {original or 'NAO IDENTIFICADO'} | {standardized}")
    lines.append("")
    lines.append(
        "Observacao: campos opcionais nao identificados permanecem nulos no dataset analitico; "
        "campos obrigatorios interrompem a transformacao."
    )
    if mapping_by_year.get(2025) and mapping_by_year[2025].professional_experience == "WorkExp":
        lines.append("")
        lines.append(
            "`YearsCodePro` nao existe no survey 2025. Para 2025 foi usado `WorkExp`, "
            "que existe no schema real. `YearsCode` tambem existe, mas representa experiencia "
            "geral de codigo e nao foi tratado como equivalente direto de experiencia profissional."
        )
    (DOCS_DIR / "schema_mapping.md").write_text("\n".join(lines), encoding="utf-8")


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def transform_year(year: int, respondent_schema, os_schema) -> tuple[int, int, FieldMapping]:
    csv_path = stackoverflow_results_path(year)
    header = read_csv_header(csv_path)
    mapping = get_required_mapping(year, header)
    output_dir = PROCESSED_DIR / "stackoverflow" / f"year={year}"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log(f"Processando survey {year}")
    respondents_count = write_batches(
        row_records(csv_path, year, mapping),
        output_dir / "survey_respondents.parquet",
        respondent_schema,
    )
    os_count = write_batches(
        os_records(csv_path, year, mapping),
        output_dir / "survey_operating_systems.parquet",
        os_schema,
    )
    log(f"{respondents_count:,} respondentes exportados".replace(",", "."))
    log(f"{os_count:,} relacoes respondente-sistema exportadas".replace(",", "."))
    return respondents_count, os_count, mapping


def main() -> int:
    ensure_directories()
    raise_csv_field_size_limit()
    try:
        respondent_schema, os_schema = pyarrow_schema()
    except ImportError as exc:
        raise PipelineError(
            "PyArrow nao encontrado. Instale dependencias com: python -m pip install -r requirements.txt"
        ) from exc

    missing = [str(stackoverflow_results_path(year)) for year in YEARS if not stackoverflow_results_path(year).exists()]
    if missing:
        fail("Arquivos brutos ausentes. Execute src/download_stackoverflow.py antes.\n" + "\n".join(missing))

    mapping_by_year: dict[int, FieldMapping] = {}
    for year in YEARS:
        _, _, mapping = transform_year(year, respondent_schema, os_schema)
        mapping_by_year[year] = mapping
    write_schema_mapping(mapping_by_year)

    raw_size = sum(stackoverflow_results_path(year).stat().st_size for year in YEARS)
    parquet_size = directory_size(PROCESSED_DIR / "stackoverflow")
    reduction = (1 - parquet_size / raw_size) * 100 if raw_size else 0
    print(f"Tamanho CSV bruto: {format_size(raw_size)}")
    print(f"Tamanho Parquet: {format_size(parquet_size)}")
    print(f"Reducao percentual: {reduction:.2f}%")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
