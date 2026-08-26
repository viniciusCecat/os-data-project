from __future__ import annotations

import csv
import hashlib
import shutil
import sys
from pathlib import Path


YEARS = (2022, 2023, 2024, 2025)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_STACKOVERFLOW_DIR = RAW_DIR / "stackoverflow"
RAW_STATCOUNTER_DIR = RAW_DIR / "statcounter"
RAW_PRICES_DIR = RAW_DIR / "prices"
DOCS_DIR = PROJECT_ROOT / "docs"
TEMP_DIR = PROJECT_ROOT / ".temp"


class PipelineError(RuntimeError):
    """Erro esperado do pipeline com mensagem legivel para o usuario."""


def log(message: str) -> None:
    print(f"[INFO] {message}", flush=True)


def fail(message: str) -> None:
    raise PipelineError(message)


def ensure_directories() -> None:
    for year in YEARS:
        (RAW_STACKOVERFLOW_DIR / f"year={year}").mkdir(parents=True, exist_ok=True)
    RAW_STATCOUNTER_DIR.mkdir(parents=True, exist_ok=True)
    RAW_PRICES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def raise_csv_field_size_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


def require_executable(name: str, install_hint: str | None = None) -> str:
    executable = shutil.which(name)
    if executable:
        return executable
    hint = f" {install_hint}" if install_hint else ""
    fail(f"Executavel obrigatorio nao encontrado: {name}.{hint}")


def require_package(import_name: str, install_name: str | None = None):
    try:
        return __import__(import_name)
    except ImportError as exc:
        package = install_name or import_name
        raise PipelineError(
            f"Pacote Python obrigatorio nao encontrado: {package}. "
            f"Instale com: python -m pip install -r requirements.txt"
        ) from exc


def format_size(num_bytes: int) -> str:
    mb = num_bytes / 1_000_000
    mib = num_bytes / (1024 * 1024)
    return f"{mb:.2f} MB ({mib:.2f} MiB)"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_git_lfs_pointer(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    with path.open("rb") as handle:
        head = handle.read(512)
    return (
        b"version https://git-lfs.github.com/spec/v1" in head
        and b"oid sha256:" in head
        and b"size " in head
    )


def read_csv_header(path: Path) -> list[str]:
    if not path.exists():
        fail(f"Arquivo esperado nao encontrado: {path}")
    if is_git_lfs_pointer(path):
        fail(f"Arquivo parece ser ponteiro Git LFS, nao CSV real: {path}")
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        try:
            return next(csv.reader(handle))
        except StopIteration as exc:
            raise PipelineError(f"CSV vazio: {path}") from exc
        except csv.Error as exc:
            raise PipelineError(f"CSV invalido em {path}: {exc}") from exc


def stackoverflow_results_path(year: int) -> Path:
    return RAW_STACKOVERFLOW_DIR / f"year={year}" / "results.csv"


def exit_with_error(exc: Exception) -> int:
    if isinstance(exc, PipelineError):
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    raise exc
