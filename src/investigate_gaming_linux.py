from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import csv
import importlib
import io
import re
from urllib.request import urlopen

from common import PROJECT_ROOT, exit_with_error, fail, require_package


STEAM_SURVEY_URL = "https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam"
STEAM_HISTORY_REPO_URL = "https://github.com/jdegene/steamHWsurvey"
SHS_CSV_URL = "https://raw.githubusercontent.com/jdegene/steamHWsurvey/master/shs.csv"
SHS_PLATFORM_CSV_URL = "https://raw.githubusercontent.com/jdegene/steamHWsurvey/master/shs_platform.csv"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
REPORT_PATH = REPORTS_DIR / "gaming_linux_trend.md"
FIGURE_PATH = FIGURES_DIR / "07_steam_linux_trend.png"

YEARS = (2022, 2023, 2024, 2025)
SYSTEMS = {
    "Windows": ("pc", "Windows Version"),
    "Linux": ("linux", "Linux Version"),
    "macOS": ("mac", "OSX Version"),
}


@dataclass(frozen=True)
class SteamEstimate:
    survey_date: str
    year: int
    system: str
    pct: float
    main_visible_pct: float
    platform_visible_pct: float
    matched_versions: int


def download_csv(url: str) -> tuple[list[dict[str, str]], int]:
    with urlopen(url, timeout=60) as response:
        content = response.read()
    text = content.decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text))), len(content)


def normalize_name(value: str) -> str:
    value = value.replace('"', "").strip()
    return re.sub(r"\s+", " ", value)


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_pp(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f} p.p."


def fmt_mb(num_bytes: int) -> str:
    return f"{num_bytes / 1_000_000:.2f} MB"


def build_main_os_map(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    by_date: dict[str, dict[str, float]] = {}
    for row in rows:
        if row["category"] != "OS Version":
            continue
        by_date.setdefault(row["date"], {})[normalize_name(row["name"])] = float(row["percentage"])
    return by_date


def build_platform_os_map(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, float]]:
    by_date_platform: dict[tuple[str, str], dict[str, float]] = {}
    category_by_platform = {platform: category for _, (platform, category) in SYSTEMS.items()}
    for row in rows:
        platform = row["platform"]
        if platform not in category_by_platform:
            continue
        if row["category"] != category_by_platform[platform]:
            continue
        key = (row["date"], platform)
        by_date_platform.setdefault(key, {})[normalize_name(row["name"])] = float(row["percentage"])
    return by_date_platform


def estimate_system_share(
    survey_date: str,
    system: str,
    main_os: dict[str, dict[str, float]],
    platform_os: dict[tuple[str, str], dict[str, float]],
) -> SteamEstimate:
    platform, _ = SYSTEMS[system]
    main_versions = main_os.get(survey_date, {})
    platform_versions = platform_os.get((survey_date, platform), {})
    matched = sorted(
        version
        for version in main_versions.keys() & platform_versions.keys()
        if version.lower() != "other"
    )
    if not matched:
        fail(f"Nenhuma versao em comum encontrada para {system} em {survey_date}.")

    main_visible = sum(main_versions[name] for name in matched)
    platform_visible = sum(platform_versions[name] for name in matched)
    if platform_visible <= 0:
        fail(f"Soma invalida na pagina de plataforma para {system} em {survey_date}.")

    return SteamEstimate(
        survey_date=survey_date,
        year=int(survey_date[:4]),
        system=system,
        pct=main_visible * 100.0 / platform_visible,
        main_visible_pct=main_visible * 100.0,
        platform_visible_pct=platform_visible * 100.0,
        matched_versions=len(matched),
    )


def estimate_all_dates(
    main_os: dict[str, dict[str, float]],
    platform_os: dict[tuple[str, str], dict[str, float]],
) -> list[SteamEstimate]:
    rows: list[SteamEstimate] = []
    for survey_date in sorted(main_os):
        if int(survey_date[:4]) < 2022:
            continue
        for system, (platform, _) in SYSTEMS.items():
            if (survey_date, platform) not in platform_os:
                continue
            try:
                rows.append(estimate_system_share(survey_date, system, main_os, platform_os))
            except Exception:
                continue
    return rows


def write_chart(monthly_rows: list[SteamEstimate]) -> None:
    require_package("matplotlib", "matplotlib")
    plt = importlib.import_module("matplotlib.pyplot")

    linux_rows = [row for row in monthly_rows if row.system == "Linux"]
    if not linux_rows:
        fail("Sem dados mensais de Linux para gerar a figura Steam.")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    x_values = [row.survey_date[:7] for row in linux_rows]
    y_values = [row.pct for row in linux_rows]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(range(len(x_values)), y_values, color="#16a34a", linewidth=2.3)
    ax.scatter(range(len(x_values)), y_values, color="#16a34a", s=16)
    tick_indexes = [index for index, label in enumerate(x_values) if label.endswith("-12") or index == len(x_values) - 1]
    ax.set_xticks(tick_indexes)
    ax.set_xticklabels([x_values[index] for index in tick_indexes], rotation=30, ha="right")
    ax.set_title("Steam Hardware Survey: tendencia de Linux entre gamers")
    ax.set_xlabel("Mes")
    ax.set_ylabel("% estimado de usuarios Steam")
    ax.grid(True, axis="y", alpha=0.25)
    ax.text(
        0.01,
        -0.28,
        "Fonte: Steam Hardware & Software Survey; historico organizado por jdegene/steamHWsurvey.",
        transform=ax.transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=160)
    plt.close(fig)


def markdown_table(rows: list[SteamEstimate]) -> str:
    lines = [
        "Ano | Windows | Linux | macOS",
        "--- | --- | --- | ---",
    ]
    by_year: dict[int, dict[str, SteamEstimate]] = {}
    for row in rows:
        by_year.setdefault(row.year, {})[row.system] = row
    for year in sorted(by_year):
        lines.append(
            f"{year} | "
            f"{fmt_pct(by_year[year]['Windows'].pct)} | "
            f"{fmt_pct(by_year[year]['Linux'].pct)} | "
            f"{fmt_pct(by_year[year]['macOS'].pct)}"
        )
    return "\n".join(lines)


def write_report(december_rows: list[SteamEstimate], monthly_rows: list[SteamEstimate], file_sizes: dict[str, int]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    linux_december = {row.year: row for row in december_rows if row.system == "Linux"}
    latest_linux = [row for row in monthly_rows if row.system == "Linux"][-1]
    linux_change = linux_december[2025].pct - linux_december[2022].pct
    relative_growth = linux_december[2025].pct / linux_december[2022].pct

    lines = f"""# Tendencia Linux entre gamers

## Fonte

A fonte gamer escolhida foi a Steam Hardware & Software Survey, pesquisa mensal oficial da Valve/Steam:

```text
{STEAM_SURVEY_URL}
```

Para ter historico em CSV, foi usado o repositorio publico `jdegene/steamHWsurvey`, que organiza dados da Steam Hardware Survey e dados antigos via Web Archive:

```text
{STEAM_HISTORY_REPO_URL}
```

Arquivos CSV consultados:

- `shs.csv`: {fmt_mb(file_sizes['shs'])}
- `shs_platform.csv`: {fmt_mb(file_sizes['platform'])}

## Metodo

A Steam mostra versoes especificas de sistema operacional na pagina geral, mas parte das versoes pode ficar escondida em `Other` ou nao aparecer no resumo principal. Por isso, esta verificacao nao soma apenas as versoes visiveis.

O calculo cruza as versoes visiveis no CSV geral com a pagina especifica de cada plataforma. Exemplo: se as distros Linux visiveis no resumo representam uma parte conhecida dentro da pagina Linux, essa proporcao e usada para estimar o total Linux.

## Resultado principal

Linux entre usuarios da Steam aumentou no periodo analisado:

- 2022-12: {fmt_pct(linux_december[2022].pct)}
- 2025-12: {fmt_pct(linux_december[2025].pct)}
- variacao: {fmt_pp(linux_change)}
- crescimento relativo: {relative_growth:.2f}x

Esse resultado combina com a tendencia corrigida do Stack Overflow: em outro publico, tambem aparece crescimento de Linux. A comparacao deve ser usada como evidencia complementar, nao como prova de causalidade.

## Dezembro de cada ano

{markdown_table(december_rows)}

## Ultimo mes disponivel no historico

- Mes: {latest_linux.survey_date[:7]}
- Linux: {fmt_pct(latest_linux.pct)}

## Interpretacao para o seminario

A conclusao que podemos defender e: depois da correcao da normalizacao, Linux cresceu no Stack Overflow; e uma fonte externa de gamers, a Steam Hardware Survey, tambem mostra crescimento de Linux entre usuarios da Steam.

Isso fortalece a pergunta de pesquisa porque mostra que a alta nao apareceu apenas dentro da nossa base principal. Mesmo assim, cada fonte mede um publico diferente:

- Stack Overflow: respondentes desenvolvedores.
- StatCounter: uso desktop observado em page views.
- Steam: usuarios da Steam que participam da pesquisa de hardware/software.

## Limitacoes

- A Steam Survey e opcional e anonima.
- Os dados historicos em CSV vem de um repositorio publico que organiza dados da Steam e Web Archive; a fonte oficial principal e a pagina da Steam.
- Usuarios da Steam nao representam todos os gamers nem todos os usuarios de desktop.
- Os percentuais sao de participacao, nao quantidade absoluta de pessoas.
- Comparar Steam com Stack Overflow e StatCounter serve para contexto, nao para causalidade.

Gerado em {date.today().isoformat()}.
"""
    REPORT_PATH.write_text(lines, encoding="utf-8")


def main() -> int:
    shs_rows, shs_size = download_csv(SHS_CSV_URL)
    platform_rows, platform_size = download_csv(SHS_PLATFORM_CSV_URL)
    main_os = build_main_os_map(shs_rows)
    platform_os = build_platform_os_map(platform_rows)

    december_rows = []
    for year in YEARS:
        survey_date = f"{year}-12-01"
        for system in SYSTEMS:
            december_rows.append(estimate_system_share(survey_date, system, main_os, platform_os))

    monthly_rows = estimate_all_dates(main_os, platform_os)
    write_chart(monthly_rows)
    write_report(december_rows, monthly_rows, {"shs": shs_size, "platform": platform_size})

    print("Steam Hardware Survey - dezembro de cada ano")
    print(markdown_table(december_rows))
    linux_2022 = next(row for row in december_rows if row.year == 2022 and row.system == "Linux")
    linux_2025 = next(row for row in december_rows if row.year == 2025 and row.system == "Linux")
    print(f"Linux 2022-12 -> 2025-12: {fmt_pct(linux_2022.pct)} -> {fmt_pct(linux_2025.pct)} ({fmt_pp(linux_2025.pct - linux_2022.pct)})")
    print(REPORT_PATH)
    print(FIGURE_PATH)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
