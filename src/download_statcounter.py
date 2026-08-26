from __future__ import annotations

import csv
import re
from datetime import date, datetime

import requests

from common import RAW_STATCOUNTER_DIR, exit_with_error, fail, log
from statcounter import normalize_statcounter_os


PAGE_URL = "https://gs.statcounter.com/os-market-share/desktop/worldwide"
CHART_URL = "https://gs.statcounter.com/chart.php"
OUTPUT = RAW_STATCOUNTER_DIR / "os_market_share.csv"
RAW_EXPORT = RAW_STATCOUNTER_DIR / "statcounter_desktop_worldwide_raw.csv"
COLUMNS = [
    "date",
    "region",
    "operating_system_original",
    "operating_system_family",
    "market_share",
    "source",
    "collected_at",
]
MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
}


def latest_month_from_page(html: str) -> str:
    match = re.search(r"Desktop Operating System Market Share Worldwide - ([A-Za-z]+) (\d{4})", html)
    if not match:
        fail("Nao foi possivel identificar o mes mais recente na pagina oficial do StatCounter.")
    month_name, year = match.groups()
    month = MONTHS.get(month_name)
    if not month:
        fail(f"Mes inesperado na pagina do StatCounter: {month_name}")
    return f"{year}-{month}"


def fetch_page() -> str:
    response = requests.get(PAGE_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        fail(f"Falha ao acessar StatCounter: HTTP {response.status_code}")
    return response.text


def fetch_csv(to_month: str) -> str:
    params = {
        "device_hidden": "desktop",
        "statType_hidden": "os_combined",
        "region_hidden": "ww",
        "granularity": "monthly",
        "statDisplay": "Desktop Operating System Market Share",
        "regionDisplay": "Worldwide",
        "fromMonthYear": "2022-01",
        "toMonthYear": to_month,
        "csv": "1",
    }
    response = requests.get(
        CHART_URL,
        params=params,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0", "Referer": PAGE_URL},
    )
    if response.status_code != 200:
        fail(f"Falha ao baixar CSV do StatCounter: HTTP {response.status_code}")
    text = response.text
    if not text.startswith('"Date",'):
        fail("Resposta do StatCounter nao parece ser CSV tabular esperado.")
    return text


def transform_csv(raw_csv: str, collected_at: str) -> int:
    rows = list(csv.DictReader(raw_csv.splitlines()))
    if not rows:
        fail("CSV do StatCounter sem linhas.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        count = 0
        for row in rows:
            row_date = datetime.strptime(row["Date"], "%Y-%m").date().replace(day=1).isoformat()
            for os_name, value in row.items():
                if os_name == "Date" or value in ("", None):
                    continue
                normalized = normalize_statcounter_os(os_name)
                market_share = float(value)
                writer.writerow(
                    {
                        "date": row_date,
                        "region": "Worldwide",
                        "operating_system_original": normalized.original,
                        "operating_system_family": normalized.family,
                        "market_share": f"{market_share:.6f}".rstrip("0").rstrip("."),
                        "source": PAGE_URL,
                        "collected_at": collected_at,
                    }
                )
                count += 1
    return count


def main() -> int:
    html = fetch_page()
    to_month = latest_month_from_page(html)
    log(f"Periodo StatCounter: 2022-01 ate {to_month}")
    raw_csv = fetch_csv(to_month)
    RAW_STATCOUNTER_DIR.mkdir(parents=True, exist_ok=True)
    RAW_EXPORT.write_text(raw_csv, encoding="utf-8")
    rows = transform_csv(raw_csv, date.today().isoformat())
    print(f"StatCounter salvo em: {OUTPUT}")
    print(f"Exportacao bruta salva em: {RAW_EXPORT}")
    print(f"Linhas normalizadas: {rows}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))

