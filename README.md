# Adocao de sistemas operacionais pagos e gratuitos

Projeto academico de Mineracao de Dados em Python.

## Pergunta de pesquisa

**Como a adocao de Windows, Linux e macOS entre desenvolvedores evoluiu nos ultimos anos, e como ela se compara considerando perfil dos usuarios, modelo de licenciamento e custo do sistema operacional?**

## Fontes

- Stack Overflow Developer Survey, via repositorio oficial `StackExchange/Survey`.
- StatCounter Global Stats desktop worldwide, por exportacao CSV oficial da pagina.
- Precos e licenciamento, por fontes oficiais registradas em `data/raw/prices/os_prices.csv`.

## Estrutura

```text
data/raw/              dados brutos imutaveis
data/processed/        Parquet e DuckDB gerados
src/                   scripts da pipeline
notebooks/             EDA e analises reproduziveis
docs/                  metodologia, fontes e schema mapping
tests/                 testes unitarios e testes opcionais de dados
```

## Instalacao

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

O download dos surveys exige Git e Git LFS. Se Git LFS nao estiver instalado, o script para com erro claro para evitar arquivos pointer.

## Execucao

```bash
python src/download_stackoverflow.py
python src/inspect_data.py
python src/transform_stackoverflow.py
python src/download_statcounter.py
python src/prepare_prices.py
python src/build_database.py
python src/validate.py
python src/analyze.py
python src/generate_figures.py
```

Se a coleta automatica do StatCounter falhar, prepare o arquivo manual:

```bash
python src/prepare_statcounter.py
```

Depois, preencha `data/raw/statcounter/os_market_share.csv` somente com dados exportados da fonte oficial.

## Resultados da validacao

Use:

```bash
python src/validate.py
```

O relatorio calcula dinamicamente:

- arquivos presentes;
- tamanho bruto em MB e MiB;
- SHA-256;
- respondentes por ano, quando DuckDB existir;
- sistemas encontrados;
- periodo e linhas do StatCounter;
- precos/licenciamento;
- problemas pendentes.

## Metodologia

O projeto segue CRISP-DM. A documentacao completa esta em `docs/crisp_dm.md`.

As tabelas analiticas sao separadas:

- `survey_respondents`
- `survey_operating_systems`
- `os_market_share`
- `os_prices`

Respostas multi-select geram mais de uma linha em `survey_operating_systems`. Portanto, os percentuais devem declarar o denominador usado.

Para percentuais de uso entre desenvolvedores, o denominador e:

```text
respondentes validos na pergunta de sistema operacional naquele ano
```

Como a pergunta aceita multiplas respostas, os percentuais por sistema podem somar mais de 100%.

StatCounter e Stack Overflow nao sao amostras equivalentes. A comparacao e exploratoria e deve ser lida como contraste entre metodologias diferentes.

## Machine Learning

ML nao e obrigatorio. Primeiro vem EDA. Um modelo so deve ser criado se responder uma pergunta defensavel sem vazamento de dados. Caso contrario, documente que ML nao agregaria resposta confiavel.

## Limitacoes

- Stack Overflow nao representa todos os usuarios de computador.
- Surveys tem vies de selecao.
- Perguntas e colunas mudam por ano.
- Respostas multi-select exigem cuidado.
- IDs nao ligam a mesma pessoa entre anos diferentes.
- Market share nao significa quantidade exata de pessoas.
- Associacao nao significa causalidade.
- Precos e licencas podem mudar e precisam de fonte oficial com data de coleta.
- Preco de software e custo/exigencia de hardware sao variaveis diferentes.
