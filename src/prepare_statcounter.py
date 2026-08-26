from __future__ import annotations

import csv
from datetime import date

from common import RAW_STATCOUNTER_DIR, exit_with_error, log


OUTPUT = RAW_STATCOUNTER_DIR / "os_market_share.csv"
README = RAW_STATCOUNTER_DIR / "README.md"
COLUMNS = [
    "date",
    "region",
    "operating_system_original",
    "operating_system_family",
    "market_share",
    "source",
    "collected_at",
]


def main() -> int:
    RAW_STATCOUNTER_DIR.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists():
        with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(COLUMNS)
        log(f"Arquivo preparado: {OUTPUT}")
    README.write_text(
        "\n".join(
            [
                "# StatCounter",
                "",
                f"Preparado em: {date.today().isoformat()}",
                "",
                "O script `src/download_statcounter.py` usa a exportacao CSV oficial acionada pelo botao `Download Data (.csv)`.",
                "Se a exportacao automatica falhar, baixe o CSV manualmente e normalize para:",
                "",
                "date,region,operating_system_original,operating_system_family,market_share,source,collected_at",
                "",
                "Arquivo esperado:",
                "",
                "`data/raw/statcounter/os_market_share.csv`",
                "",
                "Nao converta market share em numero absoluto de pessoas sem metodologia estatistica propria.",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Edite manualmente, com dados exportados da fonte, se necessario: {OUTPUT}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))
