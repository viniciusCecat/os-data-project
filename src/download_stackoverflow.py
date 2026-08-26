from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from common import (
    RAW_STACKOVERFLOW_DIR,
    TEMP_DIR,
    YEARS,
    ensure_directories,
    exit_with_error,
    fail,
    format_size,
    is_git_lfs_pointer,
    log,
    require_executable,
    sha256_file,
)


REPO_URL = "https://github.com/StackExchange/Survey.git"
DEFAULT_REPO_DIR = TEMP_DIR / "StackExchange-Survey"
RESULT_NAME_HINTS = ("results.csv", "survey_results_public.csv", "survey_results.csv")
METADATA_HINTS = ("schema", "questionnaire", "readme", "survey_results_schema")
METADATA_SUFFIXES = {".csv", ".txt", ".md", ".pdf", ".xlsx", ".json"}


def run_git(repo_dir: Path | None, args: list[str], *, env: dict[str, str] | None = None) -> str:
    cmd = ["git"]
    if repo_dir is not None:
        cmd.extend(["-C", str(repo_dir)])
    cmd.extend(args)
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        fail(f"Comando Git falhou: {' '.join(cmd)}\n{detail}")
    return proc.stdout


def run_lfs(repo_dir: Path, args: list[str]) -> str:
    cmd = ["git", "-C", str(repo_dir), "lfs", *args]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        fail(f"Comando Git LFS falhou: {' '.join(cmd)}\n{detail}")
    return proc.stdout


def ensure_source_repo(repo_dir: Path) -> None:
    require_executable("git", "Instale Git antes de executar o download.")
    if subprocess.run(["git", "lfs", "version"], capture_output=True, text=True).returncode != 0:
        fail(
            "Git LFS nao encontrado. Instale Git LFS e execute novamente; "
            "nao e seguro continuar porque os CSVs podem virar apenas arquivos pointer."
        )

    if repo_dir.exists():
        if not (repo_dir / ".git").exists():
            fail(f"Diretorio de origem existe, mas nao parece ser um repositorio Git: {repo_dir}")
        log(f"Repositorio StackExchange/Survey encontrado em {repo_dir}")
        run_git(repo_dir, ["fetch", "--all", "--prune"])
        return

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    log(f"Clonando {REPO_URL} em {repo_dir}")
    env = os.environ.copy()
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    proc = subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", REPO_URL, str(repo_dir)],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        fail(f"Falha ao clonar {REPO_URL}\n{detail}")


def list_repo_files(repo_dir: Path) -> list[str]:
    output = run_git(repo_dir, ["ls-tree", "-r", "--name-only", "HEAD"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def score_result_candidate(path: str, year: int) -> tuple[int, str] | None:
    lower = path.casefold()
    name = Path(path).name.casefold()
    if str(year) not in lower or not lower.endswith(".csv"):
        return None
    score = 0
    for hint in RESULT_NAME_HINTS:
        if name == hint:
            score += 100
        elif hint.replace(".csv", "") in name:
            score += 30
    if "public" in lower:
        score += 10
    if "schema" in lower:
        score -= 50
    if score <= 0:
        return None
    return (score, path)


def find_result_paths(files: list[str]) -> dict[int, str]:
    result: dict[int, str] = {}
    for year in YEARS:
        scored = [item for path in files if (item := score_result_candidate(path, year))]
        if not scored:
            fail(f"Nenhum CSV de resultados encontrado no repositorio para {year}.")
        scored.sort(key=lambda item: (-item[0], item[1]))
        result[year] = scored[0][1]
    return result


def find_metadata_paths(files: list[str], year: int) -> list[str]:
    selected = []
    for path in files:
        lower = path.casefold()
        suffix = Path(path).suffix.casefold()
        if str(year) not in lower:
            continue
        if suffix not in METADATA_SUFFIXES:
            continue
        if any(hint in lower for hint in METADATA_HINTS):
            selected.append(path)
    return selected


def checkout_paths(repo_dir: Path, paths: list[str]) -> None:
    log(f"Selecionando {len(paths)} arquivo(s) no sparse checkout")
    run_git(repo_dir, ["sparse-checkout", "init", "--no-cone"])
    run_git(repo_dir, ["sparse-checkout", "set", *paths])
    run_git(repo_dir, ["checkout"])
    materialized = [(repo_dir / path).exists() and not is_git_lfs_pointer(repo_dir / path) for path in paths]
    if all(materialized):
        log("Arquivos selecionados ja estao materializados; Git LFS pull nao e necessario")
        return
    include = ",".join(paths)
    run_lfs(repo_dir, ["pull", f"--include={include}"])


def copy_immutable(source: Path, destination: Path, *, overwrite: bool) -> None:
    if not source.exists():
        fail(f"Arquivo esperado nao apareceu apos checkout: {source}")
    if is_git_lfs_pointer(source):
        fail(f"Arquivo ainda e ponteiro Git LFS, nao CSV real: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if is_git_lfs_pointer(destination):
            fail(f"Arquivo bruto existente e ponteiro Git LFS: {destination}")
        if not overwrite:
            if sha256_file(source) != sha256_file(destination):
                fail(
                    f"Arquivo bruto ja existe e difere da origem: {destination}. "
                    "Use --overwrite somente se voce decidiu substituir o raw conscientemente."
                )
            return
    shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", type=Path, default=DEFAULT_REPO_DIR)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    ensure_directories()
    ensure_source_repo(args.repo_dir)
    files = list_repo_files(args.repo_dir)
    result_paths = find_result_paths(files)
    metadata_paths = sorted({path for year in YEARS for path in find_metadata_paths(files, year)})
    checkout_paths(args.repo_dir, sorted(set(result_paths.values()) | set(metadata_paths)))

    total = 0
    for year, rel_path in result_paths.items():
        source = args.repo_dir / rel_path
        destination = RAW_STACKOVERFLOW_DIR / f"year={year}" / "results.csv"
        copy_immutable(source, destination, overwrite=args.overwrite)
        size = destination.stat().st_size
        total += size
        print(f"{year} | arquivo encontrado | tamanho: {format_size(size)} | sha256: {sha256_file(destination)}")

        for meta_rel_path in find_metadata_paths(files, year):
            meta_source = args.repo_dir / meta_rel_path
            if meta_source.exists() and not is_git_lfs_pointer(meta_source):
                copy_immutable(meta_source, destination.parent / Path(meta_rel_path).name, overwrite=args.overwrite)

    print(f"Total bruto: {format_size(total)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
