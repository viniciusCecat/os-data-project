from __future__ import annotations

from datetime import date
import importlib
from pathlib import Path

from common import PROCESSED_DIR, PROJECT_ROOT, exit_with_error, fail, require_package


DB_PATH = PROCESSED_DIR / "project.duckdb"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
FIGURE_PATH = FIGURES_DIR / "06_trend_investigation.png"
REPORT_PATH = REPORTS_DIR / "trend_investigation.md"
SYSTEMS = ("Windows", "Linux", "macOS")


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_pp(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f} p.p."


def query_stackoverflow(con):
    return con.execute(
        """
        WITH valid AS (
            SELECT survey_year,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS valid_respondents
            FROM survey_operating_systems
            GROUP BY survey_year
        ),
        counts AS (
            SELECT survey_year,
                   operating_system_family,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS users
            FROM survey_operating_systems
            WHERE operating_system_family IN ('Windows', 'Linux', 'macOS')
            GROUP BY survey_year, operating_system_family
        )
        SELECT c.survey_year,
               c.operating_system_family,
               valid.valid_respondents,
               c.users,
               c.users * 100.0 / valid.valid_respondents AS pct
        FROM counts c
        JOIN valid USING (survey_year)
        ORDER BY c.survey_year, c.operating_system_family
        """
    ).fetchall()


def query_statcounter(con):
    return con.execute(
        """
        SELECT year(date) AS survey_year,
               operating_system_family,
               avg(market_share) AS pct
        FROM os_market_share
        WHERE operating_system_family IN ('Windows', 'Linux', 'macOS')
          AND year(date) BETWEEN 2022 AND 2025
        GROUP BY year(date), operating_system_family
        ORDER BY survey_year, operating_system_family
        """
    ).fetchall()


def query_linux_variant_tokens(con):
    return con.execute(
        """
        SELECT survey_year,
               operating_system_original,
               count(*) AS selections
        FROM survey_operating_systems
        WHERE operating_system_original IN (
            'Other Linux-based',
            'Linux (non-WSL)',
            'Red Hat',
            'NixOS',
            'Pop!_OS'
        )
        GROUP BY survey_year, operating_system_original
        ORDER BY survey_year, selections DESC, operating_system_original
        """
    ).fetchall()


def build_nested(rows):
    nested: dict[int, dict[str, dict[str, float | int]]] = {}
    for year, system, valid, users, pct in rows:
        nested.setdefault(year, {})[system] = {
            "valid": int(valid),
            "users": int(users),
            "pct": float(pct),
        }
    return nested


def build_statcounter_nested(rows):
    nested: dict[int, dict[str, float]] = {}
    for year, system, pct in rows:
        nested.setdefault(int(year), {})[system] = float(pct)
    return nested


def pct(data, year: int, system: str) -> float:
    return float(data[year][system]["pct"])


def users(data, year: int, system: str) -> int:
    return int(data[year][system]["users"])


def valid(data, year: int) -> int:
    return int(next(iter(data[year].values()))["valid"])


def yoy_rows(data) -> list[tuple[int, str, float]]:
    rows = []
    years = sorted(data)
    for previous, current in zip(years, years[1:]):
        for system in SYSTEMS:
            rows.append((current, system, pct(data, current, system) - pct(data, previous, system)))
    return rows


def write_chart(data) -> None:
    require_package("matplotlib", "matplotlib")
    plt = importlib.import_module("matplotlib.pyplot")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    years = sorted(data)
    colors = {"Windows": "#2563eb", "Linux": "#16a34a", "macOS": "#9333ea"}

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for system in SYSTEMS:
        values = [pct(data, year, system) for year in years]
        ax.plot(years, values, marker="o", linewidth=2.4, label=system, color=colors[system])
        for year, value in zip(years, values):
            y_offset = -18 if system == "macOS" else 8
            ax.annotate(f"{value:.1f}%", (year, value), textcoords="offset points", xytext=(0, y_offset), ha="center", fontsize=8)

    ax.set_title("Stack Overflow: sistemas operacionais usados por respondentes validos")
    ax.set_xlabel("Ano")
    ax.set_ylabel("% de respondentes validos")
    ax.set_xticks(years)
    ax.set_ylim(0, 65)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=160)
    plt.close(fig)


def evidence_table(data) -> str:
    lines = [
        "Ano | Windows | Linux | macOS | Respondentes válidos",
        "--- | --- | --- | --- | ---",
    ]
    for year in sorted(data):
        lines.append(
            f"{year} | "
            f"{fmt_int(users(data, year, 'Windows'))} ({fmt_pct(pct(data, year, 'Windows'))}) | "
            f"{fmt_int(users(data, year, 'Linux'))} ({fmt_pct(pct(data, year, 'Linux'))}) | "
            f"{fmt_int(users(data, year, 'macOS'))} ({fmt_pct(pct(data, year, 'macOS'))}) | "
            f"{fmt_int(valid(data, year))}"
        )
    return "\n".join(lines)


def yoy_table(data) -> str:
    lines = [
        "Ano | Sistema | Diferença vs. ano anterior",
        "--- | --- | ---",
    ]
    for year, system, diff in yoy_rows(data):
        lines.append(f"{year} | {system} | {fmt_pp(diff)}")
    return "\n".join(lines)


def statcounter_table(statcounter) -> str:
    lines = [
        "Ano | Windows | Linux | macOS",
        "--- | --- | --- | ---",
    ]
    for year in sorted(statcounter):
        lines.append(
            f"{year} | "
            f"{fmt_pct(statcounter[year]['Windows'])} | "
            f"{fmt_pct(statcounter[year]['Linux'])} | "
            f"{fmt_pct(statcounter[year]['macOS'])}"
        )
    return "\n".join(lines)


def linux_variant_table(rows) -> str:
    lines = [
        "Ano | Valor original | Seleções",
        "--- | --- | ---",
    ]
    for year, original, selections in rows:
        lines.append(f"{year} | {original} | {fmt_int(int(selections))}")
    return "\n".join(lines)


def write_report(data, statcounter, linux_variants) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    linux_2022 = pct(data, 2022, "Linux")
    linux_2023 = pct(data, 2023, "Linux")
    linux_2025 = pct(data, 2025, "Linux")
    linux_change_2023 = linux_2023 - linux_2022
    linux_net = linux_2025 - linux_2022
    windows_net = pct(data, 2025, "Windows") - pct(data, 2022, "Windows")
    macos_net = pct(data, 2025, "macOS") - pct(data, 2022, "macOS")
    stat_linux_net = statcounter[2025]["Linux"] - statcounter[2022]["Linux"]
    variant_total = sum(int(row[2]) for row in linux_variants)

    today = date.today().isoformat()
    lines = f"""# Investigação de tendência

## 1. Descobertas encontradas

1. Linux teve a maior mudança clara após corrigir a normalização: passou de {fmt_pct(linux_2022)} em 2022 para {fmt_pct(linux_2025)} em 2025 ({fmt_pp(linux_net)}).
2. Windows ficou praticamente estável no período completo: {fmt_pct(pct(data, 2022, "Windows"))} em 2022 e {fmt_pct(pct(data, 2025, "Windows"))} em 2025 ({fmt_pp(windows_net)}).
3. macOS também ficou quase estável: {fmt_pct(pct(data, 2022, "macOS"))} em 2022 e {fmt_pct(pct(data, 2025, "macOS"))} em 2025 ({fmt_pp(macos_net)}).

## 2. Descoberta escolhida

A descoberta escolhida foi que a primeira leitura dos dados subestimava Linux porque algumas respostas claramente relacionadas a Linux estavam caindo em `Other`.

Ela foi escolhida porque mostra um ponto central de mineração de dados: antes de interpretar uma tendência, é preciso auditar a qualidade da normalização. Depois da correção, Linux deixa de parecer queda e passa a ser a maior alta entre os três sistemas.

## 3. Evidência no Stack Overflow

{evidence_table(data)}

Os percentuais usam como denominador os respondentes que responderam validamente à pergunta de sistema operacional naquele ano. Como a pergunta permite respostas múltiplas, os percentuais podem somar mais de 100%.

Diferença em pontos percentuais entre anos:

{yoy_table(data)}

## 4. Hipóteses

1. A alta de Linux pode representar aumento real de uso entre respondentes do Stack Overflow.
2. Parte da mudança pode estar ligada à forma como as opções do survey aparecem nos anos mais recentes.
3. Parte da mudança pode estar ligada à normalização: distribuições ou variantes Linux precisam ser agrupadas na família Linux.
4. A tendência dos desenvolvedores pode ser diferente da tendência do mercado desktop geral.

## 5. Hipótese investigada

A hipótese investigada foi: a aparente queda inicial de Linux era um artefato de preparação dos dados. Ao reclassificar respostas explicitamente Linux, como `Other Linux-based`, `Linux (non-WSL)`, `Red Hat`, `NixOS` e `Pop!_OS`, a tendência correta mostra crescimento de Linux entre os respondentes.

## 6. Fontes externas

- nome: StackExchange/Survey - arquivos oficiais do Stack Overflow Developer Survey
- link: https://github.com/StackExchange/Survey/tree/main/packages/archive
- data: consultado em {today}
- dado ou fato encontrado: o repositório oficial mantém, por ano, `results.csv` e `schema.csv`; os schemas registram a pergunta `OpSys` sobre o sistema operacional primário usado no trabalho.
- relação com a hipótese: confirma que a análise usa arquivos oficiais e que a pergunta de sistema operacional vem do survey original.

- nome: Valores originais encontrados nos CSVs do Stack Overflow
- link: dados locais extraídos dos `results.csv` oficiais
- data: consultado em {today}
- dado ou fato encontrado: foram encontradas {fmt_int(variant_total)} seleções em valores explicitamente Linux que precisavam ficar na família Linux.
- relação com a hipótese: esses valores explicam por que a classificação anterior jogava parte do Linux em `Other`.

- nome: StatCounter Desktop OS Market Share Worldwide
- link: https://gs.statcounter.com/os-market-share/desktop/worldwide
- data: consultado em {today}
- dado ou fato encontrado: nos dados coletados pelo projeto, Linux no mercado desktop geral passou de {fmt_pct(statcounter[2022]["Linux"])} em 2022 para {fmt_pct(statcounter[2025]["Linux"])} em 2025 ({fmt_pp(stat_linux_net)}).
- relação com a hipótese: a direção do StatCounter também é de crescimento, embora em outro público e com outra metodologia.

- nome: StatCounter FAQ / metodologia
- link: https://gs.statcounter.com/faq
- data: consultado em {today}
- dado ou fato encontrado: o StatCounter calcula estatísticas a partir de page views em mais de 1 milhão de sites e mais de 3 bilhões de page views por mês, analisando sistema operacional por page view.
- relação com a hipótese: mostra que o StatCounter mede mercado/uso web geral, uma população diferente do Stack Overflow.

## 7. Comparação

Valores originais reclassificados como Linux:

{linux_variant_table(linux_variants)}

Tabela externa do StatCounter, média anual no mercado desktop geral:

{statcounter_table(statcounter)}

Linha do tempo:

2022
- Stack Overflow Linux: {fmt_pct(pct(data, 2022, "Linux"))}
- Stack Overflow Windows: {fmt_pct(pct(data, 2022, "Windows"))}
- StatCounter Linux desktop: {fmt_pct(statcounter[2022]["Linux"])}

2023
- Stack Overflow Linux: {fmt_pct(pct(data, 2023, "Linux"))}
- Stack Overflow Windows: {fmt_pct(pct(data, 2023, "Windows"))}
- StatCounter Linux desktop: {fmt_pct(statcounter[2023]["Linux"])}
- Fato relevante: aparecem valores como `Other Linux-based` e `Red Hat`, que precisam ser tratados como Linux.

2024
- Stack Overflow Linux: {fmt_pct(pct(data, 2024, "Linux"))}
- Stack Overflow Windows: {fmt_pct(pct(data, 2024, "Windows"))}
- StatCounter Linux desktop: {fmt_pct(statcounter[2024]["Linux"])}
- Fato relevante: `Other Linux-based` e `Red Hat` continuam aparecendo entre os valores originais.

2025
- Stack Overflow Linux: {fmt_pct(pct(data, 2025, "Linux"))}
- Stack Overflow Windows: {fmt_pct(pct(data, 2025, "Windows"))}
- StatCounter Linux desktop: {fmt_pct(statcounter[2025]["Linux"])}
- Fato relevante: aparece `Linux (non-WSL)`, além de distribuições como `NixOS` e `Pop!_OS`.

Os dados apoiam a hipótese de que havia um problema de preparação: tokens explicitamente Linux estavam fora da família Linux. Depois da correção, Linux cresce no Stack Overflow de {fmt_pct(linux_2022)} para {fmt_pct(linux_2025)}. O StatCounter também mostra crescimento de Linux no desktop geral, mas essa comparação é apenas contextual porque as fontes medem populações diferentes.

## 8. Conclusão

Nos dados corrigidos do Stack Overflow, Linux cresceu de {fmt_pct(linux_2022)} em 2022 para {fmt_pct(linux_2025)} em 2025. Essa é a tendência mais interessante entre os três sistemas analisados.

O ponto principal da investigação é que a conclusão anterior seria enganosa sem auditar `Other`. O crescimento fica claro depois que variantes Linux são classificadas corretamente. A comparação com o StatCounter reforça que Linux também cresce no mercado desktop geral, mas não prova que as duas tendências tenham a mesma causa.

## 9. Limitações

- A análise não prova causalidade.
- Stack Overflow representa respondentes da comunidade de desenvolvimento, não todos os usuários de computador.
- StatCounter mede page views em sites participantes, não respondentes individuais.
- StatCounter e Stack Overflow medem populações diferentes.
- Respostas de sistema operacional podem permitir múltiplos sistemas; por isso os percentuais podem somar mais de 100%.
- Mudanças de schema e de formulação de perguntas entre anos podem afetar comparações.
- A reclassificação cobre apenas valores explicitamente Linux encontrados nos dados; outros valores em `Other` devem continuar sendo tratados com cautela.

## 10. Roteiro para apresentação

Quando exploramos nossa base, primeiro parecia que Linux tinha caído. Mas isso ficou estranho, então auditamos a categoria `Other`. Nessa auditoria encontramos respostas como `Other Linux-based`, `Linux (non-WSL)`, `Red Hat`, `NixOS` e `Pop!_OS`, que são claramente ligadas a Linux.

Depois de corrigir a normalização, Linux passou de {fmt_pct(linux_2022)} em 2022 para {fmt_pct(linux_2025)} em 2025, uma alta de {fmt_pp(linux_net)}. Windows e macOS ficaram quase estáveis no mesmo período.

Para comparar com uma fonte externa, usamos o StatCounter. Lá, Linux no mercado desktop geral também aumentou, de {fmt_pct(statcounter[2022]["Linux"])} em 2022 para {fmt_pct(statcounter[2025]["Linux"])} em 2025. Essa comparação ajuda como contexto, mas não prova causalidade porque StatCounter e Stack Overflow medem populações diferentes.

Nossa conclusão é que a descoberta principal não é apenas que Linux cresceu. A descoberta mais importante é metodológica: sem limpar corretamente os valores originais, parte do Linux ficava escondida em `Other` e a interpretação ficava errada. Isso mostra por que a preparação dos dados é uma etapa essencial antes da análise.
"""
    REPORT_PATH.write_text(lines, encoding="utf-8")


def print_summary(data, statcounter) -> None:
    print("Ano | Windows | Linux | macOS | Respondentes validos")
    print("--- | --- | --- | --- | ---")
    for year in sorted(data):
        print(
            f"{year} | "
            f"{fmt_int(users(data, year, 'Windows'))} ({fmt_pct(pct(data, year, 'Windows'))}) | "
            f"{fmt_int(users(data, year, 'Linux'))} ({fmt_pct(pct(data, year, 'Linux'))}) | "
            f"{fmt_int(users(data, year, 'macOS'))} ({fmt_pct(pct(data, year, 'macOS'))}) | "
            f"{fmt_int(valid(data, year))}"
        )
    print()
    print("Variacao 2022-2025:")
    for system in SYSTEMS:
        print(f"{system}: {fmt_pp(pct(data, 2025, system) - pct(data, 2022, system))}")
    print(f"StatCounter Linux 2022-2025: {fmt_pp(statcounter[2025]['Linux'] - statcounter[2022]['Linux'])}")
    print(f"Grafico: {FIGURE_PATH}")
    print(f"Relatorio: {REPORT_PATH}")


def main() -> int:
    if not DB_PATH.exists():
        fail("Banco DuckDB ausente. Execute src/build_database.py antes.")
    duckdb = require_package("duckdb")
    require_package("pandas")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        stackoverflow = build_nested(query_stackoverflow(con))
        statcounter = build_statcounter_nested(query_statcounter(con))
        linux_variants = query_linux_variant_tokens(con)
    finally:
        con.close()

    write_chart(stackoverflow)
    write_report(stackoverflow, statcounter, linux_variants)
    print_summary(stackoverflow, statcounter)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
