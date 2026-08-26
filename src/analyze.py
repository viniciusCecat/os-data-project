from __future__ import annotations

from common import PROCESSED_DIR, exit_with_error, fail, require_package


DB_PATH = PROCESSED_DIR / "project.duckdb"


def print_rows(title: str, rows, columns: list[str], limit: int | None = 20) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        print("Sem dados disponiveis.")
        return
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    selected_rows = rows if limit is None else rows[:limit]
    for row in selected_rows:
        print(" | ".join("" if value is None else str(value) for value in row))


def has_column(con, table: str, column: str) -> bool:
    rows = con.execute(f"PRAGMA table_info('{table}')").fetchall()
    return any(row[1] == column for row in rows)


def main() -> int:
    if not DB_PATH.exists():
        fail("Banco DuckDB ausente. Execute src/build_database.py antes.")
    duckdb = require_package("duckdb")
    con = duckdb.connect(str(DB_PATH), read_only=True)

    print("Denominador dos percentuais Stack Overflow: respondentes com resposta valida de sistema operacional no ano.")
    print("Respostas multi-select podem gerar mais de um sistema por respondente; percentuais podem somar mais de 100%.")

    print_rows(
        "A. Sistemas mais frequentes entre desenvolvedores",
        con.execute(
            """
            SELECT operating_system_family, count(*) AS selecoes
            FROM survey_operating_systems
            GROUP BY operating_system_family
            ORDER BY selecoes DESC, operating_system_family
            """
        ).fetchall(),
        ["sistema", "selecoes"],
    )

    print_rows(
        "B. Evolucao Windows, Linux e macOS",
        con.execute(
            """
            WITH denom AS (
                SELECT survey_year,
                       count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS respondents
                FROM survey_operating_systems
                GROUP BY survey_year
            )
            SELECT os.survey_year,
                   os.operating_system_family,
                   count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS respondents_using,
                   round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / denom.respondents, 2) AS pct_respondents
            FROM survey_operating_systems os
            JOIN denom USING (survey_year)
            WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS')
            GROUP BY os.survey_year, os.operating_system_family, denom.respondents
            ORDER BY os.survey_year, os.operating_system_family
            """
        ).fetchall(),
        ["ano", "familia", "respondentes", "pct"],
    )

    print_rows(
        "C. Diferenca por pais - top combinacoes",
        con.execute(
            """
            SELECT r.country,
                   os.operating_system_family,
                   count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS respondents
            FROM survey_operating_systems os
            JOIN survey_respondents r USING (survey_year, respondent_id)
            WHERE r.country IS NOT NULL
            GROUP BY r.country, os.operating_system_family
            ORDER BY respondents DESC, r.country, os.operating_system_family
            LIMIT 20
            """
        ).fetchall(),
        ["pais", "familia", "respondentes"],
    )

    brazil_count = con.execute(
        """
        SELECT count(DISTINCT survey_year::VARCHAR || ':' || respondent_id)
        FROM survey_respondents
        WHERE country IN ('Brazil', 'Brasil')
        """
    ).fetchone()[0]
    if brazil_count >= 100:
        print_rows(
            "C. Brasil",
            con.execute(
                """
                SELECT os.survey_year, os.operating_system_family,
                       count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS respondents
                FROM survey_operating_systems os
                JOIN survey_respondents r USING (survey_year, respondent_id)
                WHERE r.country IN ('Brazil', 'Brasil')
                GROUP BY os.survey_year, os.operating_system_family
                ORDER BY os.survey_year, respondents DESC
                """
            ).fetchall(),
            ["ano", "familia", "respondentes"],
            limit=None,
        )
    else:
        print("\n=== C. Brasil ===")
        print(f"Amostra insuficiente pelo criterio configurado: {brazil_count} respondentes (< 100).")

    if has_column(con, "survey_respondents", "employment"):
        print_rows(
            "D. Perfil profissional vs outros",
            con.execute(
                """
                SELECT CASE
                           WHEN regexp_matches(
                               employment,
                               '(^|;)\\s*(Employed, full-time|Employed, part-time|Independent contractor, freelancer, or self-employed)\\s*(;|$)'
                           ) THEN 'profissional'
                           WHEN employment IS NULL THEN 'nao informado'
                           ELSE 'outros'
                       END AS perfil,
                       os.operating_system_family,
                       count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) AS respondents
                FROM survey_operating_systems os
                JOIN survey_respondents r USING (survey_year, respondent_id)
                GROUP BY perfil, os.operating_system_family
                ORDER BY perfil, respondents DESC
                """
            ).fetchall(),
            ["perfil", "familia", "respondentes"],
        )

    print_rows(
        "E. Anos de experiencia",
        con.execute(
            """
            SELECT professional_experience,
                   operating_system_family,
                   count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS respondents
            FROM survey_operating_systems
            JOIN survey_respondents USING (survey_year, respondent_id)
            WHERE professional_experience IS NOT NULL
            GROUP BY professional_experience, operating_system_family
            ORDER BY respondents DESC
            LIMIT 20
            """
        ).fetchall(),
        ["experiencia", "familia", "respondentes"],
    )

    print("\n=== F. Comparacao com StatCounter ===")
    market_share_rows = con.execute("SELECT count(*) FROM os_market_share").fetchone()[0]
    if market_share_rows == 0:
        print("Sem dados StatCounter carregados. Use data/raw/statcounter/os_market_share.csv.")
    else:
        print_rows(
            "F. Stack Overflow vs StatCounter - media anual",
            con.execute(
                """
                WITH so_denom AS (
                    SELECT survey_year,
                           count(DISTINCT survey_year::VARCHAR || ':' || respondent_id) AS respondents
                    FROM survey_operating_systems
                    GROUP BY survey_year
                ),
                so AS (
                    SELECT os.survey_year AS year,
                           os.operating_system_family,
                           round(count(DISTINCT os.survey_year::VARCHAR || ':' || os.respondent_id) * 100.0 / so_denom.respondents, 2) AS stackoverflow_pct
                    FROM survey_operating_systems os
                    JOIN so_denom USING (survey_year)
                    WHERE os.operating_system_family IN ('Windows', 'Linux', 'macOS', 'ChromeOS')
                    GROUP BY os.survey_year, os.operating_system_family, so_denom.respondents
                ),
                sc AS (
                    SELECT year(date) AS year,
                           operating_system_family,
                           round(avg(market_share), 2) AS statcounter_desktop_pct
                    FROM os_market_share
                    WHERE operating_system_family IN ('Windows', 'Linux', 'macOS', 'ChromeOS')
                    GROUP BY year(date), operating_system_family
                )
                SELECT so.year,
                       so.operating_system_family,
                       so.stackoverflow_pct,
                       sc.statcounter_desktop_pct
                FROM so
                LEFT JOIN sc USING (year, operating_system_family)
                ORDER BY so.year, so.operating_system_family
                """
            ).fetchall(),
            ["ano", "familia", "stackoverflow_pct", "statcounter_desktop_pct"],
            limit=None,
        )
    print("Nota metodologica: Stack Overflow mede respondentes; StatCounter mede participacao observada pela fonte.")

    print_rows(
        "G. Modelos de licenca cadastrados",
        con.execute(
            """
            SELECT system,
                   edition,
                   open_source,
                   license_model,
                   software_price,
                   currency,
                   support_model,
                   hardware_required,
                   source
            FROM os_prices
            ORDER BY system, edition
            """
        ).fetchall(),
        ["sistema", "edicao", "open_source", "licenca", "preco", "moeda", "suporte", "hardware", "fonte"],
        limit=None,
    )
    con.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
