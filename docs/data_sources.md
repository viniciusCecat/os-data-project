# Fontes de dados

## Stack Overflow Developer Survey

Fonte principal: repositorio oficial `StackExchange/Survey`.

O script `src/download_stackoverflow.py` clona o repositorio via Git, exige Git LFS e copia os CSVs reais para `data/raw/stackoverflow/year=YYYY/results.csv`.

Anos previstos inicialmente:

- 2022
- 2023
- 2024
- 2025

Os arquivos brutos nao devem ser editados. Hashes SHA-256 e tamanhos sao calculados no momento do download e da validacao.

## StatCounter Global Stats

Fonte secundaria para comparar a pesquisa com uso geral de sistemas operacionais desktop.

Pagina oficial usada:

```text
https://gs.statcounter.com/os-market-share/desktop/worldwide
```

A pagina oficial oferece `Download Data (.csv)`. O script `src/download_statcounter.py` confirmou no JavaScript oficial que essa exportacao usa `chart.php` com os parametros do grafico e `csv=1`; por isso a coleta automatica usa a propria exportacao do site, sem Selenium/Playwright.

Periodo coletado:

```text
2022-01 ate o mes mais recente identificado na pagina oficial
```

Granularidade:

```text
mensal
```

Arquivos:

- `data/raw/statcounter/statcounter_desktop_worldwide_raw.csv`: CSV bruto retornado pela exportacao oficial;
- `data/raw/statcounter/os_market_share.csv`: CSV normalizado em formato longo.

Se a exportacao automatica falhar, o fluxo manual e:

1. acessar a pagina de market share desejada;
2. exportar CSV pela propria interface da fonte;
3. salvar os dados normalizados em `data/raw/statcounter/os_market_share.csv`;
4. manter `source` preenchido com a URL consultada.

Schema esperado:

```text
date,region,operating_system_original,operating_system_family,market_share,source,collected_at
```

Market share nao e numero exato de pessoas e nao deve ser convertido automaticamente para populacao.

## Precos e licenciamento

Arquivo preparado: `data/raw/prices/os_prices.csv`.

Schema:

```text
collected_at,system,edition,license_model,open_source,software_price,currency,hardware_required,support_model,source,notes
```

Regras:

- usar apenas fontes oficiais;
- registrar a data da coleta;
- diferenciar preco do software e exigencia de hardware;
- nao atribuir o preco de um Mac ao macOS;
- registrar preco `0` somente quando a fonte confirmar gratuidade do software;
- suporte pago de uma distribuicao Linux nao torna Linux obrigatoriamente pago.

Fontes oficiais usadas:

- Microsoft Store Windows 11 Home: `https://www.microsoft.com/en-us/d/windows-11-home/dg7gmgf0krt0`
- Microsoft Store Windows 11 Pro: `https://www.microsoft.com/en-us/d/windows-11-pro/dg7gmgf0d8h4`
- Apple Support macOS: `https://support.apple.com/en-us/102662`
- Ubuntu Desktop: `https://ubuntu.com/desktop`
- Ubuntu Pro: `https://ubuntu.com/pro`
- Ubuntu Pro pricing: `https://ubuntu.com/pricing/pro`
- Red Hat Store: `https://www.redhat.com/en/store/linux-platforms`
- ChromeOS Flex: `https://chromeos.google/intl/en_uk/products/chromeos-flex/`
- FreeBSD: `https://www.freebsd.org/`
