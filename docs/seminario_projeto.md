# Seminario do projeto

## Titulo

Adocao de sistemas operacionais entre desenvolvedores e mercado desktop geral.

## Pergunta de pesquisa

Como a adocao de Windows, Linux e macOS entre desenvolvedores evoluiu entre 2022 e 2025, e como ela se compara com o mercado desktop geral e com uma fonte complementar de gamers?

## O que queremos descobrir

O projeto pretende identificar se o comportamento dos desenvolvedores e diferente do mercado desktop geral. Apos a limpeza dos dados, a verificacao principal passou a ser entender se Linux realmente cresceu entre desenvolvedores. Para reforcar a interpretacao, usamos tambem uma fonte complementar de gamers, a Steam Hardware & Software Survey.

Mais importante que "provar uma hipotese", o foco do seminario e mostrar o aprendizado ao lidar com bancos reais:

- bases diferentes medem publicos diferentes;
- schemas mudam entre anos;
- respostas multi-select exigem cuidado;
- normalizacao ruim pode mudar a conclusao;
- uma mudanca interessante encontrada foi o crescimento de Linux.

## Fontes de dados

Fonte | Link | Uso
--- | --- | ---
Stack Overflow Developer Survey | https://github.com/StackExchange/Survey | Dados principais sobre respondentes, pais, perfil, experiencia e sistemas operacionais usados profissionalmente.
StatCounter Desktop OS Market Share | https://gs.statcounter.com/os-market-share/desktop/worldwide | Comparacao com a participacao geral de sistemas operacionais em desktops.
Steam Hardware & Software Survey | https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam | Fonte complementar para verificar a tendencia de Linux entre usuarios da Steam/gamers.
Historico Steam em CSV | https://github.com/jdegene/steamHWsurvey | Historico estruturado usado para calcular a evolucao de Linux na Steam.

## Tamanho dos dados

Os dados brutos principais do Stack Overflow somam aproximadamente 568 MB:

Ano | Tamanho
--- | ---
2022 | 108.83 MB
2023 | 158.63 MB
2024 | 159.53 MB
2025 | 140.89 MB
Total | 567.88 MB

Como existem fontes com metodologias diferentes, o foco do projeto nao e apenas volume, mas comparacao cuidadosa entre publicos diferentes.

Fonte gamer complementar:

Arquivo | Tamanho aproximado
--- | ---
Steam `shs.csv` | 4.10 MB
Steam `shs_platform.csv` | 26.99 MB
Total Steam complementar | 31.09 MB

## Estrutura inicial dos dados

O Stack Overflow Developer Survey vem em arquivos CSV anuais. Cada ano pode ter colunas diferentes, por isso o projeto inspeciona os cabecalhos reais antes da transformacao.

O StatCounter fornece dados em CSV com participacao mensal por sistema operacional no mercado desktop.

A Steam Hardware & Software Survey fornece percentuais mensais de hardware e software dos usuarios da Steam. Para obter historico comparavel, o projeto usa um CSV publico que organiza os dados da pesquisa e dados antigos via Web Archive.

## Maior esforco esperado

- Mapear colunas que mudam entre anos do survey.
- Tratar respostas multi-select, como `Windows;Ubuntu;macOS`.
- Normalizar nomes de sistemas operacionais para familias comparaveis.
- Comparar fontes que nao medem exatamente a mesma coisa.
- Explicar a Steam como evidencia complementar, nao como prova causal.

## Descoberta para destacar no seminario

A primeira leitura subestimava Linux porque alguns valores claramente Linux caiam em `Other`, como `Other Linux-based`, `Linux (non-WSL)`, `Red Hat`, `NixOS` e `Pop!_OS`.

Depois da correcao:

- Stack Overflow: Linux cresceu de 43.54% em 2022 para 50.72% em 2025;
- StatCounter desktop geral: Linux cresceu de 2.69% em 2022 para 4.16% em 2025;
- Steam/gamers: Linux cresceu de 1.38% em 2022-12 para 3.57% em 2025-12.

Essa comparacao nao prova causalidade. Ela mostra que a tendencia aparece em fontes diferentes e que a etapa de preparacao dos dados foi decisiva.

## Possiveis caminhos para explicar a mudanca

O projeto nao afirma uma causa unica, mas levanta caminhos defensaveis:

- entre desenvolvedores, Linux pode aparecer mais por uso em desenvolvimento, servidores, containers e ferramentas abertas;
- no Stack Overflow, a mudanca tambem depende da forma como as opcoes aparecem no survey e de como elas sao normalizadas;
- na Steam, a presenca de SteamOS Holo dentro dos usuarios Linux sugere investigar o efeito do ecossistema SteamOS/Steam Deck;
- no desktop geral, o crescimento existe, mas e menor que entre desenvolvedores.

## Metodologia CRISP-DM

Etapa | Aplicacao no projeto
--- | ---
Business Understanding | Entender a diferenca de adocao de sistemas operacionais entre desenvolvedores, mercado geral e uma fonte complementar de gamers.
Data Understanding | Avaliar Stack Overflow Survey, StatCounter e Steam Survey, seus schemas, tamanhos, periodos e limitacoes.
Data Preparation | Baixar CSVs, validar arquivos, mapear colunas reais, normalizar sistemas e gerar base analitica.
Modeling | Nesta etapa inicial, o foco e analise exploratoria. Machine Learning fica para uma fase futura, se houver pergunta adequada.
Evaluation | Validar dados, testar normalizacao, checar duplicidades e comparar resultados com cuidado metodologico.
Deployment | Entrega futura pode incluir notebooks, relatorio, graficos, dashboard ou API, dependendo da evolucao do projeto.

## Analises planejadas

- Evolucao de Windows, Linux e macOS entre 2022 e 2025.
- Comparacao entre Stack Overflow e StatCounter.
- Comparacao complementar com Steam para verificar a tendencia de Linux entre gamers.
- Recorte por pais, incluindo Brasil quando houver amostra suficiente.
- Diferenca por perfil profissional e experiencia, usando apenas campos existentes nos dados reais.

## Limitacoes

- Stack Overflow representa respondentes da comunidade de desenvolvimento, nao todos os usuarios de computador.
- StatCounter mede participacao observada no mercado desktop, nao respondentes individuais.
- Steam mede usuarios da Steam que participam da pesquisa, nao todos os gamers.
- As metodologias das duas fontes sao diferentes.
- Respostas multi-select podem fazer percentuais somarem mais de 100%.
- Os IDs dos surveys nao identificam a mesma pessoa ao longo dos anos.

## Resposta curta para apresentar

Nosso projeto compara a adocao de sistemas operacionais usando bancos com metodologias diferentes. Usamos o Stack Overflow Developer Survey de 2022 a 2025 como fonte principal, o StatCounter como comparacao de mercado desktop e a Steam Survey como fonte complementar para gamers. O principal aprendizado foi que a limpeza dos dados muda a interpretacao: respostas Linux estavam caindo em `Other`. Depois da normalizacao correta, Linux aparece em crescimento. A metodologia segue CRISP-DM, com foco em entendimento do problema, coleta, limpeza, transformacao e analise exploratoria.
