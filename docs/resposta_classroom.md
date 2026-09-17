# Resposta direta para a tarefa do Classroom

## 1. Ideia do projeto

Tema:

```text
Adocao de sistemas operacionais entre desenvolvedores, mercado desktop geral e usuarios da Steam.
```

O projeto analisa o uso de Windows, Linux e macOS em bases com publicos diferentes.

## 2. Pergunta de pesquisa

```text
Como a adocao de Windows, Linux e macOS evoluiu entre desenvolvedores de 2022 a 2025, e essa tendencia aparece tambem no mercado desktop geral e em usuarios da Steam?
```

## 3. O que queremos descobrir

Queremos descobrir:

- se Linux cresceu entre desenvolvedores;
- se Windows, Linux e macOS se comportam de forma diferente entre desenvolvedores e usuarios comuns;
- se uma fonte gamer, a Steam, mostra uma tendencia parecida;
- quais cuidados de limpeza e metodologia sao necessarios antes de interpretar os dados.

O ponto mais interessante encontrado ate agora:

```text
Linux parecia menor porque algumas respostas Linux estavam classificadas como Other. Depois da normalizacao correta, Linux aparece em crescimento.
```

## 4. Onde o projeto pode chegar

Nesta primeira etapa, o foco e analise exploratoria e estruturacao dos dados.

Caminhos futuros possiveis:

- criar um dashboard com a evolucao dos sistemas operacionais;
- criar uma API para consultar percentuais por ano/fonte;
- treinar um modelo apenas se surgir uma pergunta preditiva defensavel;
- comparar com outras fontes, como pesquisas de mercado ou bases de jogos;
- aprofundar a analise de Linux, SteamOS, Steam Deck e desenvolvimento de software.

Machine Learning nao e o foco inicial porque a pergunta atual e mais descritiva/comparativa.

## 5. Fontes dos dados

Fonte | Link | O que representa | Uso no projeto
--- | --- | --- | ---
Stack Overflow Developer Survey | https://github.com/StackExchange/Survey | Respondentes da comunidade de desenvolvimento | Fonte principal
StatCounter Desktop OS Market Share | https://gs.statcounter.com/os-market-share/desktop/worldwide | Participacao de sistemas desktop por page views | Comparacao com mercado geral
Steam Hardware & Software Survey | https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam | Usuarios da Steam/gamers | Fonte complementar
Historico Steam em CSV | https://github.com/jdegene/steamHWsurvey | Historico estruturado da Steam Survey | Calcular tendencia historica da Steam

## 6. Tamanho aproximado dos dados

Fonte | Tamanho aproximado
--- | ---
Stack Overflow 2022 | 108.83 MB
Stack Overflow 2023 | 158.63 MB
Stack Overflow 2024 | 159.53 MB
Stack Overflow 2025 | 140.89 MB
Total Stack Overflow | 567.88 MB
StatCounter | 0.04 MB
Steam `shs.csv` | 4.10 MB
Steam `shs_platform.csv` | 26.99 MB
Total Steam | 31.09 MB

## 7. Estrutura inicial dos dados

### Stack Overflow

Formato inicial:

```text
CSV anual, um arquivo results.csv por ano.
```

Exemplos de campos usados:

- identificador do respondente;
- pais;
- sistema operacional;
- emprego/perfil;
- experiencia;
- outros campos do questionario.

Observacao:

```text
Cada ano pode ter colunas diferentes, entao o projeto inspeciona os schemas reais antes de transformar.
```

### StatCounter

Formato inicial:

```text
CSV mensal com participacao de sistemas operacionais desktop.
```

Campos principais:

- data;
- sistema operacional;
- market share;
- regiao;
- fonte.

### Steam

Formato inicial:

```text
CSV historico com percentuais da Steam Hardware Survey.
```

Campos principais:

- data;
- plataforma;
- categoria;
- nome do sistema/versao;
- percentual.

## 8. Tecnicas que exigem mais esforco

- Mapear colunas que mudam entre anos do Stack Overflow.
- Validar que os arquivos baixados sao CSVs reais.
- Tratar respostas com multiplos sistemas operacionais.
- Normalizar nomes diferentes para familias comparaveis.
- Evitar comparar fontes como se medissem a mesma populacao.
- Separar conclusao exploratoria de causalidade.

Exemplo pratico:

```text
Other Linux-based, Linux (non-WSL), Red Hat, NixOS e Pop!_OS precisaram ser classificados como Linux, nao como Other.
```

## 9. Metodologia CRISP-DM

Etapa | Aplicacao no projeto
--- | ---
Business Understanding | Entender a diferenca de uso de sistemas operacionais entre desenvolvedores, desktop geral e gamers.
Data Understanding | Estudar fontes, schemas, tamanhos, anos disponiveis e limitacoes.
Data Preparation | Baixar CSVs, validar arquivos, mapear colunas, normalizar sistemas e gerar tabelas analiticas.
Modeling | Nesta fase, nao e prioridade. Primeiro fazemos analise exploratoria.
Evaluation | Validar resultados, testes de normalizacao, comparacao entre fontes e revisao das limitacoes.
Deployment | Futuramente, notebooks, relatorios, dashboard ou API.

## 10. Resultado exploratorio para destacar

Stack Overflow, desenvolvedores:

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 55.99% | 43.54% | 36.00%
2023 | 54.52% | 45.69% | 36.63%
2024 | 55.43% | 47.51% | 35.16%
2025 | 56.14% | 50.72% | 35.96%

Recorte Brasil dentro do Stack Overflow:

O dado do Brasil vem da propria base Stack Overflow Developer Survey. Ele foi obtido filtrando o campo de pais (`Country`) para `Brazil` ou `Brasil`, considerando apenas respondentes com resposta valida na pergunta de sistema operacional.

Ano | n Brasil | Windows | Linux | macOS
--- | --- | --- | --- | ---
2022 | 2.003 | 54.07% | 50.82% | 28.76%
2023 | 1.878 | 52.82% | 52.13% | 27.96%
2024 | 1.257 | 55.77% | 54.42% | 26.17%
2025 | 655 | 52.98% | 54.20% | 32.52%

Esse recorte e complementar. Ele nao e outra base e nao deve substituir a analise global, porque a amostra brasileira e menor.

StatCounter, desktop geral:

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 79.05% | 2.69% | 7.93%
2023 | 73.18% | 3.24% | 9.98%
2024 | 77.34% | 4.38% | 8.03%
2025 | 77.76% | 4.16% | 8.19%

Steam, gamers:

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 96.14% | 1.38% | 2.45%
2023 | 96.41% | 1.94% | 1.62%
2024 | 96.33% | 2.05% | 1.40%
2025 | 94.23% | 3.57% | 2.19%

Conclusao parcial:

```text
Linux cresce nas tres leituras, mas cada fonte mede um publico diferente. A conclusao principal e metodologica: antes de interpretar tendencia, e necessario limpar e entender a origem dos dados.
```

## 11. O que apresentar em 10 minutos com 3 pessoas

### Pessoa 1: problema, pergunta e fontes

Falar:

```text
Queremos comparar a adocao de sistemas operacionais em publicos diferentes: desenvolvedores, desktop geral e usuarios da Steam.
```

Mostrar:

- pergunta de pesquisa;
- links das bases;
- tamanho dos dados.

### Pessoa 2: metodologia, estrutura e limpeza

Falar:

```text
Seguimos CRISP-DM: entendimento do problema, entendimento dos dados, preparacao, analise exploratoria e avaliacao.
```

Mostrar:

- fluxo CRISP-DM;
- schema mapping;
- notebooks.
- valores reclassificados;
- grafico do Stack Overflow.

### Pessoa 3: resultados, Brasil, comparacao e caminhos futuros

Falar:

```text
StatCounter e Steam tambem mostram Linux crescendo, mas medem publicos diferentes. Isso nao prova causalidade, mas abre caminho para investigar motivos como desenvolvimento, ferramentas abertas, SteamOS e Steam Deck.
```

Mostrar:

- comparacao com StatCounter;
- recorte Brasil;
- grafico da Steam;
- limitacoes.

## 12. Frase final para a apresentacao

```text
O projeto mostrou que trabalhar com dados reais exige mais do que baixar CSVs. Foi necessario entender o schema de cada ano, normalizar respostas e respeitar a metodologia de cada fonte. A mudanca mais interessante foi o crescimento de Linux, mas o principal aprendizado foi que a preparacao dos dados pode mudar completamente a interpretacao.
```
