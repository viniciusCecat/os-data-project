# Guia de apresentacao e prints

## Ideia central

O projeto nao precisa ser apresentado como "provar uma hipotese perfeita". A melhor apresentacao e sobre o aprendizado ao trabalhar com bases diferentes.

Ideia principal:

```text
Ao comparar Stack Overflow, StatCounter e Steam, percebemos que cada banco mede um publico diferente. O aprendizado principal foi que a limpeza e a metodologia da fonte mudam a interpretacao. A mudanca mais interessante encontrada foi o crescimento do Linux.
```

Frase curta:

```text
Analisamos Stack Overflow Developer Survey de 2022 a 2025. No começo parecia que Linux tinha caido, mas a auditoria mostrou que respostas claramente Linux estavam indo para Other. Depois da normalizacao correta, Linux cresce entre desenvolvedores. StatCounter e Steam aparecem como fontes externas de contexto e tambem mostram crescimento de Linux.
```

## O que foi removido ou reclassificado

Os CSVs brutos nao foram apagados nem editados. Eles continuam em `data/raw/`.

Na transformacao, o projeto seleciona apenas os campos necessarios para analise:

- ano;
- id do respondente;
- sistema operacional;
- pais;
- perfil/emprego;
- experiencia, quando o campo existe no ano.

O ponto importante nao foi remover pessoas, foi corrigir a classificacao de valores que estavam indo para `Other`, mas eram Linux.

Valores reclassificados como Linux:

Ano | Valor original | Selecoes
--- | --- | ---
2023 | Other Linux-based | 6.712
2023 | Red Hat | 4.043
2024 | Other Linux-based | 4.697
2024 | Red Hat | 2.858
2025 | Linux (non-WSL) | 5.261
2025 | Red Hat | 1.789
2025 | NixOS | 570
2025 | Pop!_OS | 338

Total reclassificado: 26.268 selecoes.

Como explicar:

```text
A gente nao inventou coluna nem mudou dado bruto. A gente so normalizou nomes equivalentes. Se a resposta dizia Red Hat, NixOS, Pop!_OS ou Linux non-WSL, ela precisava entrar na familia Linux, nao em Other.
```

## Dados principais para apresentar

### Stack Overflow

Ano | Windows | Linux | macOS | Respondentes validos na pergunta de SO
--- | --- | --- | --- | ---
2022 | 55.99% | 43.54% | 36.00% | 65.503
2023 | 54.52% | 45.69% | 36.63% | 78.587
2024 | 55.43% | 47.51% | 35.16% | 52.973
2025 | 56.14% | 50.72% | 35.96% | 28.883

Conclusao:

```text
Linux cresceu de 43.54% para 50.72%, aumento de +7.17 pontos percentuais.
```

### Brasil no Stack Overflow

De onde veio:

```text
O Brasil nao e outra base. E um recorte da propria base Stack Overflow, filtrando o campo Country para Brazil/Brasil e mantendo apenas respondentes com resposta valida de sistema operacional.
```

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 54.07% | 50.82% | 28.76%
2023 | 52.82% | 52.13% | 27.96%
2024 | 55.77% | 54.42% | 26.17%
2025 | 52.98% | 54.20% | 32.52%

Amostra Brasil:

Ano | n
--- | ---
2022 | 2.003
2023 | 1.878
2024 | 1.257
2025 | 655

Como explicar:

```text
No recorte Brasil, Linux tambem aparece forte entre respondentes, mas a amostra e menor. Por isso usamos como recorte complementar, nao como conclusao principal.
```

### StatCounter desktop geral

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 79.05% | 2.69% | 7.93%
2023 | 73.18% | 3.24% | 9.98%
2024 | 77.34% | 4.38% | 8.03%
2025 | 77.76% | 4.16% | 8.19%

Conclusao:

```text
No desktop geral, Linux tambem sobe de 2.69% para 4.16%, mas essa fonte mede page views, nao respondentes.
```

### Steam gamers

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 96.14% | 1.38% | 2.45%
2023 | 96.41% | 1.94% | 1.62%
2024 | 96.33% | 2.05% | 1.40%
2025 | 94.23% | 3.57% | 2.19%

Conclusao:

```text
Entre usuarios da Steam, Linux cresceu de 1.38% para 3.57%, aumento de +2.19 pontos percentuais.
```

Observacao importante:

```text
SteamOS Holo esta contado dentro de Linux. Em 2025, Linux e 3.57% do total da Steam; dentro dos usuarios Linux, SteamOS Holo representa 26.32%. Isso equivale a cerca de 0.94% do total da Steam.
```

## Tamanhos dos dados

Fonte | Tamanho aproximado
--- | ---
Stack Overflow 2022 | 108.83 MB
Stack Overflow 2023 | 158.63 MB
Stack Overflow 2024 | 159.53 MB
Stack Overflow 2025 | 140.89 MB
Total Stack Overflow | 567.88 MB
StatCounter CSV | 0.04 MB
Steam `shs.csv` | 4.10 MB
Steam `shs_platform.csv` | 26.99 MB
Total Steam complementar | 31.09 MB

Como explicar:

```text
O maior volume esta no Stack Overflow. StatCounter e Steam entram mais como comparacao de tendencia do que como volume de dados.
```

## Links para colar na planilha

```text
https://github.com/StackExchange/Survey
https://gs.statcounter.com/os-market-share/desktop/worldwide
https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam
https://github.com/jdegene/steamHWsurvey
```

## Notebooks

### Notebook 01 - Exploracao

Arquivo:

```text
notebooks/01_exploration.ipynb
```

O que ele mostra:

- verifica se os CSVs brutos existem;
- mostra cabecalhos reais de 2022, 2023, 2024 e 2025;
- prova que a analise partiu dos arquivos reais.

Print bom:

```text
Print da primeira celula executada mostrando 2022, 2023, 2024 e 2025 como True e os caminhos dos results.csv.
```

### Notebook 02 - Sistemas operacionais

Arquivo:

```text
notebooks/02_operating_systems.ipynb
```

O que ele mostra:

- consultas no DuckDB sobre sistemas operacionais;
- contagens e percentuais por ano;
- ajuda a explicar Windows, Linux e macOS.

Print bom:

```text
Print da tabela com Linux crescendo por ano ou do grafico de sistemas operacionais.
```

### Notebook 03 - Analise

Arquivo:

```text
notebooks/03_analysis.ipynb
```

O que ele mostra:

- execucao das analises A-G;
- versao em notebook do que o script src/analyze.py tambem imprime;
- bom para mostrar que o projeto e reproduzivel.

Print bom:

```text
Print do grafico principal ou do relatorio que mostra a reclassificacao de valores Linux.
```

### Notebook 04 - Comparacao entre bancos e aprendizado

Arquivo:

```text
notebooks/04_external_sources.ipynb
```

Este e o notebook mais importante para a apresentacao agora.

O que ele mostra:

- Stack Overflow como fonte de desenvolvedores;
- valores Linux que foram reclassificados;
- StatCounter como fonte de desktop geral;
- Steam como fonte complementar de gamers;
- possiveis motivos/caminhos de investigacao, como SteamOS Holo dentro do Linux na Steam;
- graficos prontos para print.

Print bom:

```text
Print das secoes 1 a 4, mostrando Stack Overflow, valores reclassificados, StatCounter e Steam.
```

Outro print bom:

```text
Print da secao 5, "Possiveis motivos ou caminhos de investigacao".
```

## Prints recomendados para os slides

Use estes prints, nessa ordem:

1. `docs/seminario_projeto.md`: pergunta de pesquisa e fontes.
2. `notebooks/01_exploration.ipynb`: CSVs reais encontrados.
3. `notebooks/04_external_sources.ipynb`: comparacao entre Stack Overflow, StatCounter e Steam.
4. `reports/figures/06_trend_investigation.png`: grafico principal do Stack Overflow.
5. `notebooks/04_external_sources.ipynb`: tabela dos valores reclassificados como Linux.
6. `reports/figures/07_steam_linux_trend.png`: Steam/gamers.
7. Terminal com `python src/validate.py`: mostrar `Problemas encontrados: 0`.

Nao precisa mostrar tudo no slide. Escolha 4 ou 5 prints bons:

- pergunta/fontes;
- notebook provando dados reais;
- notebook 04 comparando bancos;
- grafico Stack Overflow;
- tabela de reclassificacao;
- grafico Steam.

## Como tirar prints

No VS Code:

1. abra o notebook;
2. clique em `Run All`;
3. deixe a saida mais importante visivel;
4. use a ferramenta de captura do sistema.

No terminal Linux, opcoes comuns:

```bash
gnome-screenshot -a
```

ou, se tiver KDE/Spectacle:

```bash
spectacle -r
```

ou, se tiver Flameshot:

```bash
flameshot gui
```

Se nao souber qual existe:

```bash
which gnome-screenshot spectacle flameshot
```

## Roteiro para 3 pessoas em 10 minutos

### Pessoa 1 - Problema, pergunta e fontes, 3 minutos

Falar:

```text
Nosso projeto investiga a adocao de sistemas operacionais olhando bases diferentes. A fonte principal e Stack Overflow Developer Survey, que representa desenvolvedores. Para comparar metodologia e contexto, usamos StatCounter como desktop geral e Steam como fonte complementar gamer.
```

Mostrar:

- slide com pergunta;
- links das fontes;
- tamanho dos dados.

### Pessoa 2 - Metodologia, dados e limpeza, 3 minutos

Falar:

```text
Seguimos CRISP-DM: entendimento do problema, coleta, entendimento dos dados, preparacao, analise e avaliacao. A parte mais trabalhosa foi lidar com schemas diferentes por ano e respostas multi-select.
```

Mostrar:

- `docs/crisp_dm.md`;
- `docs/schema_mapping.md`;
- print do notebook 01.
- tabela de reclassificacao;
- grafico `06_trend_investigation.png`.

### Pessoa 3 - Resultados, Brasil, comparacao e conclusao, 4 minutos

Falar:

```text
No Stack Overflow, Linux cresceu de 43.54% para 50.72%. No recorte Brasil, Linux tambem aparece forte, mas a amostra e menor. No StatCounter, Linux tambem cresce no desktop geral. Na Steam, Linux cresce entre gamers de 1.38% para 3.57%. A conclusao e que a mudanca aparece em fontes diferentes, mas cada fonte mede um publico diferente. Por isso, o certo e falar em tendencia e aprendizado metodologico, nao em causalidade.
```

Mostrar:

- grafico Stack Overflow vs StatCounter;
- grafico Brasil vs global, se houver tempo;
- grafico Steam;
- validacao final.

## Perguntas que o professor pode fazer

### Os dados vieram de onde?

Resposta:

```text
Stack Overflow veio do repositorio oficial StackExchange/Survey. StatCounter veio da pagina oficial de market share desktop. Steam veio da pagina oficial Steam Hardware Survey e do historico CSV publico jdegene/steamHWsurvey.
```

### Voces rasparam a pagina?

Resposta:

```text
Nao no Stack Overflow. Baixamos os arquivos oficiais. No StatCounter usamos a exportacao CSV oficial. Na Steam usamos um historico em CSV que organiza os dados publicados pela propria Steam e por Web Archive.
```

### Por que os percentuais do Stack Overflow somam mais de 100%?

Resposta:

```text
Porque a pergunta aceita multiplos sistemas operacionais. Um mesmo respondente pode usar Windows e Linux, por exemplo.
```

### Por que Steam nao esta no DuckDB principal?

Resposta:

```text
Porque Steam mede outro publico. Para nao misturar metodologias, deixamos como investigacao complementar em relatorio separado.
```

### O projeto prova que Linux esta vencendo Windows?

Resposta:

```text
Nao. O projeto mostra crescimento de Linux nas fontes analisadas. Windows continua muito forte. A conclusao e sobre tendencia e qualidade da preparacao dos dados, nao sobre causalidade ou substituicao total.
```
