# Investigação de tendência

## 1. Descobertas encontradas

1. Linux teve a maior mudança clara após corrigir a normalização: passou de 43.54% em 2022 para 50.72% em 2025 (+7.17 p.p.).
2. Windows ficou praticamente estável no período completo: 55.99% em 2022 e 56.14% em 2025 (+0.15 p.p.).
3. macOS também ficou quase estável: 36.00% em 2022 e 35.96% em 2025 (-0.04 p.p.).

## 2. Descoberta escolhida

A descoberta escolhida foi que a primeira leitura dos dados subestimava Linux porque algumas respostas claramente relacionadas a Linux estavam caindo em `Other`.

Ela foi escolhida porque mostra um ponto central de mineração de dados: antes de interpretar uma tendência, é preciso auditar a qualidade da normalização. Depois da correção, Linux deixa de parecer queda e passa a ser a maior alta entre os três sistemas.

## 3. Evidência no Stack Overflow

Ano | Windows | Linux | macOS | Respondentes válidos
--- | --- | --- | --- | ---
2022 | 36.674 (55.99%) | 28.523 (43.54%) | 23.578 (36.00%) | 65.503
2023 | 42.844 (54.52%) | 35.906 (45.69%) | 28.786 (36.63%) | 78.587
2024 | 29.365 (55.43%) | 25.167 (47.51%) | 18.625 (35.16%) | 52.973
2025 | 16.215 (56.14%) | 14.649 (50.72%) | 10.385 (35.96%) | 28.883

Os percentuais usam como denominador os respondentes que responderam validamente à pergunta de sistema operacional naquele ano. Como a pergunta permite respostas múltiplas, os percentuais podem somar mais de 100%.

Diferença em pontos percentuais entre anos:

Ano | Sistema | Diferença vs. ano anterior
--- | --- | ---
2023 | Windows | -1.47 p.p.
2023 | Linux | +2.14 p.p.
2023 | macOS | +0.63 p.p.
2024 | Windows | +0.92 p.p.
2024 | Linux | +1.82 p.p.
2024 | macOS | -1.47 p.p.
2025 | Windows | +0.71 p.p.
2025 | Linux | +3.21 p.p.
2025 | macOS | +0.80 p.p.

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
- data: consultado em 2026-11-15
- dado ou fato encontrado: o repositório oficial mantém, por ano, `results.csv` e `schema.csv`; os schemas registram a pergunta `OpSys` sobre o sistema operacional primário usado no trabalho.
- relação com a hipótese: confirma que a análise usa arquivos oficiais e que a pergunta de sistema operacional vem do survey original.

- nome: Valores originais encontrados nos CSVs do Stack Overflow
- link: dados locais extraídos dos `results.csv` oficiais
- data: consultado em 2026-11-15
- dado ou fato encontrado: foram encontradas 26.268 seleções em valores explicitamente Linux que precisavam ficar na família Linux.
- relação com a hipótese: esses valores explicam por que a classificação anterior jogava parte do Linux em `Other`.

- nome: StatCounter Desktop OS Market Share Worldwide
- link: https://gs.statcounter.com/os-market-share/desktop/worldwide
- data: consultado em 2026-11-15
- dado ou fato encontrado: nos dados coletados pelo projeto, Linux no mercado desktop geral passou de 2.69% em 2022 para 4.16% em 2025 (+1.47 p.p.).
- relação com a hipótese: a direção do StatCounter também é de crescimento, embora em outro público e com outra metodologia.

- nome: StatCounter FAQ / metodologia
- link: https://gs.statcounter.com/faq
- data: consultado em 2026-11-15
- dado ou fato encontrado: o StatCounter calcula estatísticas a partir de page views em mais de 1 milhão de sites e mais de 3 bilhões de page views por mês, analisando sistema operacional por page view.
- relação com a hipótese: mostra que o StatCounter mede mercado/uso web geral, uma população diferente do Stack Overflow.

## 7. Comparação

Valores originais reclassificados como Linux:

Ano | Valor original | Seleções
--- | --- | ---
2023 | Other Linux-based | 6.712
2023 | Red Hat | 4.043
2024 | Other Linux-based | 4.697
2024 | Red Hat | 2.858
2025 | Linux (non-WSL) | 5.261
2025 | Red Hat | 1.789
2025 | NixOS | 570
2025 | Pop!_OS | 338

Tabela externa do StatCounter, média anual no mercado desktop geral:

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 79.05% | 2.69% | 7.93%
2023 | 73.18% | 3.24% | 9.98%
2024 | 77.34% | 4.38% | 8.03%
2025 | 77.76% | 4.16% | 8.19%

Linha do tempo:

2022
- Stack Overflow Linux: 43.54%
- Stack Overflow Windows: 55.99%
- StatCounter Linux desktop: 2.69%

2023
- Stack Overflow Linux: 45.69%
- Stack Overflow Windows: 54.52%
- StatCounter Linux desktop: 3.24%
- Fato relevante: aparecem valores como `Other Linux-based` e `Red Hat`, que precisam ser tratados como Linux.

2024
- Stack Overflow Linux: 47.51%
- Stack Overflow Windows: 55.43%
- StatCounter Linux desktop: 4.38%
- Fato relevante: `Other Linux-based` e `Red Hat` continuam aparecendo entre os valores originais.

2025
- Stack Overflow Linux: 50.72%
- Stack Overflow Windows: 56.14%
- StatCounter Linux desktop: 4.16%
- Fato relevante: aparece `Linux (non-WSL)`, além de distribuições como `NixOS` e `Pop!_OS`.

Os dados apoiam a hipótese de que havia um problema de preparação: tokens explicitamente Linux estavam fora da família Linux. Depois da correção, Linux cresce no Stack Overflow de 43.54% para 50.72%. O StatCounter também mostra crescimento de Linux no desktop geral, mas essa comparação é apenas contextual porque as fontes medem populações diferentes.

## 8. Conclusão

Nos dados corrigidos do Stack Overflow, Linux cresceu de 43.54% em 2022 para 50.72% em 2025. Essa é a tendência mais interessante entre os três sistemas analisados.

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

Depois de corrigir a normalização, Linux passou de 43.54% em 2022 para 50.72% em 2025, uma alta de +7.17 p.p.. Windows e macOS ficaram quase estáveis no mesmo período.

Para comparar com uma fonte externa, usamos o StatCounter. Lá, Linux no mercado desktop geral também aumentou, de 2.69% em 2022 para 4.16% em 2025. Essa comparação ajuda como contexto, mas não prova causalidade porque StatCounter e Stack Overflow medem populações diferentes.

Nossa conclusão é que a descoberta principal não é apenas que Linux cresceu. A descoberta mais importante é metodológica: sem limpar corretamente os valores originais, parte do Linux ficava escondida em `Other` e a interpretação ficava errada. Isso mostra por que a preparação dos dados é uma etapa essencial antes da análise.
