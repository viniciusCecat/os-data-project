# Roteiro da apresentação - 3 pessoas

Duração alvo: 12 a 13 minutos.  
Limite seguro: até 15 minutos.

Integrantes:

- Vinicius Cecatto
- Leonardo Scheffer Nunes
- Rafael Alves

Divisão:

- Vinicius: problema, fontes, coleta e pipeline.
- Leonardo: CRISP-DM, limpeza exploratória e validação inicial.
- Rafael: resultados exploratórios, comparação, limitações e próximos passos.

## Slide 1 - Abertura

Responsável: Vinicius  
Tempo: 35 a 40 segundos

```text
Bom dia. Nosso projeto é sobre adoção de sistemas operacionais. A gente compara Windows, Linux e macOS em três leituras diferentes: desenvolvedores, mercado desktop geral e usuários da Steam. O grupo hoje está com três integrantes: Vinicius, Leonardo e Rafael. Nesta etapa, o foco não é vender uma conclusão definitiva, mas mostrar uma proposta bem estruturada e uma análise exploratória inicial com dados reais.
```

## Slide 2 - Pergunta

Responsável: Vinicius  
Tempo: 45 segundos

```text
A pergunta principal é: como Windows, Linux e macOS evoluíram entre desenvolvedores de 2022 a 2025, e se essa tendência aparece também em outras fontes. O ponto importante é que cada fonte mede um público diferente, então a comparação precisa ser feita com cuidado. O que chamou atenção no processo foi o crescimento de Linux depois que os dados foram limpos corretamente.
```

## Slide 3 - Fontes

Responsável: Vinicius  
Tempo: 1 minuto

```text
Usamos o Stack Overflow Developer Survey como fonte principal, porque ele traz respostas de desenvolvedores e tem CSVs anuais grandes. Para comparação com o mercado geral, usamos o StatCounter Desktop OS Market Share. E para uma fonte complementar de gamers, usamos a Steam Hardware Survey junto com um histórico em CSV. O recorte Brasil não é outra base: ele vem do próprio Stack Overflow, filtrando a coluna Country.
```

## Slide 4 - Mapa das fontes

Responsável: Vinicius  
Tempo: 55 segundos

```text
Esse slide mostra por que a gente não trata todos os links como se fossem iguais. O Stack Overflow responde o que desenvolvedores dizem usar. O StatCounter ajuda a comparar com o desktop geral. A Steam serve como uma fonte complementar para observar o público gamer e o efeito de Linux e SteamOS. Então a comparação é exploratória: ela olha direção de tendência, não diz que as bases medem exatamente a mesma população.
```

## Slide 5 - Coleta

Responsável: Vinicius  
Tempo: 55 segundos

```text
Um cuidado nosso foi não usar só o visual das páginas. Os dados do Stack Overflow foram baixados como arquivos oficiais do Developer Survey. Depois a gente conferiu se os CSVs eram arquivos reais, e não ponteiros do Git LFS. Também validamos tamanho e hash. Isso é importante porque, se a coleta estiver errada, todo gráfico depois fica comprometido.
```

## Slide 6 - Pipeline

Responsável: Vinicius  
Tempo: 1 minuto e 10 segundos

```text
O pipeline transforma os CSVs brutos em uma base analítica. Primeiro vem a inspeção dos schemas reais, porque o Stack Overflow muda colunas entre anos. Depois vem a transformação, onde tratamos respostas multi-select e agrupamos os sistemas em famílias como Windows, Linux e macOS. Em seguida geramos Parquet, DuckDB, notebooks e relatórios. O principal aprendizado aqui é que dado bruto não fala sozinho; antes de interpretar tendência, precisa entender como a resposta foi registrada.
```

## Slide 7 - CRISP-DM

Responsável: Leonardo  
Tempo: 55 segundos

```text
A metodologia usada foi CRISP-DM. Nesta etapa do seminário, já avançamos em três partes: definição do problema, entendimento dos dados e preparação inicial. A preparação inclui baixar, validar, mapear colunas e normalizar os sistemas operacionais. As etapas seguintes ficam como futuro: modelagem, se fizer sentido para uma pergunta mais específica, avaliação mais aprofundada dos achados e uma entrega como dashboard.
```

## Slide 8 - Limpeza exploratória

Responsável: Leonardo  
Tempo: 1 minuto e 15 segundos

```text
Durante a exploração, encontramos um desafio importante: parte do Linux estava escondida em Other. Ao auditar os valores originais, apareceram respostas como Other Linux-based, Linux non-WSL, Red Hat, NixOS e Pop!_OS. Esses valores não foram inventados, eles já estavam no CSV. A preparação inicial reclassificou 26.268 seleções para a família Linux. Isso não fecha o projeto, mas mostra por que a limpeza muda a leitura exploratória.
```

## Slide 9 - Validação

Responsável: Leonardo  
Tempo: 50 segundos

```text
A gente também validou o projeto para não depender só da impressão de que o código estava certo. Conferimos arquivos reais, tamanho e SHA-256, documentamos o mapeamento de colunas reais por ano, geramos DuckDB e rodamos testes. Isso evita apresentar um gráfico bonito construído em cima de dado mal interpretado.
```

## Slide 10 - Stack Overflow

Responsável: Rafael  
Tempo: 1 minuto

```text
Aqui está o resultado principal no Stack Overflow. Depois da normalização correta, Linux cresce de 43,54% em 2022 para 50,72% em 2025. Windows fica relativamente estável, perto de 55%, e macOS oscila perto de 36%. Como a pergunta de sistema operacional é multi-select, os percentuais podem somar mais de 100%.
```

## Slide 11 - Brasil

Responsável: Rafael  
Tempo: 1 minuto

```text
O Brasil aparece como recorte dentro do Stack Overflow. Ele é útil para discussão, mas precisa de cuidado, porque a amostra brasileira é menor, principalmente em 2025, com 655 respondentes válidos na pergunta de sistema operacional. Mesmo assim, o recorte mostra Linux forte no Brasil e permite comparar com o conjunto global sem tratar isso como uma base independente.
```

## Slide 12 - Comparação entre fontes

Responsável: Rafael  
Tempo: 1 minuto

```text
Neste gráfico usamos índice, porque as escalas originais são muito diferentes. Stack Overflow mede respondentes desenvolvedores, StatCounter mede market share desktop e Steam mede usuários participantes da pesquisa. Então a comparação aqui não é de percentual absoluto, mas de direção da tendência. Nas três fontes, Linux cresce no período analisado.
```

## Slide 13 - Steam

Responsável: Rafael  
Tempo: 55 segundos

```text
Na Steam, Linux também cresce: sai de 1,38% em 2022 para 3,57% em 2025. SteamOS Holo está dentro da família Linux. Em 2025, ele equivale a cerca de 0,94% do total da Steam. Isso não prova que SteamOS é a única causa, mas dá um caminho interessante para investigar o crescimento de Linux entre gamers.
```

## Slide 14 - Limitações

Responsável: Rafael  
Tempo: 55 segundos

```text
Aqui a gente deixa claro o que não pode afirmar ainda. As fontes medem públicos diferentes, a pergunta do Stack Overflow é multi-select, o recorte Brasil tem amostra menor em 2025 e crescimento não prova automaticamente uma causa única. Mostrar essas limitações é importante porque deixa a análise mais honesta e mais defensável.
```

## Slide 15 - Resultados exploratórios e próximos passos

Responsável: Rafael, com Vinicius fechando se quiser  
Tempo: 50 segundos

```text
Como resultado exploratório, Linux aparece em crescimento no Stack Overflow, e essa direção também aparece em StatCounter e Steam. Mas isso ainda não é uma conclusão definitiva. O principal aprendizado foi metodológico: trabalhar com bancos reais exige entender fonte, schema, limpeza e limitação. Como próximos passos, o projeto pode evoluir para dashboard, análise por país e perfil, possível modelagem se surgir uma pergunta adequada e investigação mais profunda sobre SteamOS.
```

Fechamento curto para Vinicius:

```text
Então, nesta etapa, mais importante que encerrar a resposta foi deixar uma base preparada e caminhos claros para aprofundar.
```

## Tempo estimado

Pessoa | Slides | Tempo aproximado
--- | --- | ---
Vinicius | 1 a 6 | 5 min 25 s
Leonardo | 7 a 9 | 3 min
Rafael | 10 a 15 | 5 min 40 s
Total | 15 slides | 14 min 05 s com pausas

## Se o ensaio passar de 15 minutos

Cortes mais fáceis:

- Cortar metade da fala do slide 4.
- No slide 11, não comentar todos os números do Brasil; falar só que é recorte e que a amostra é menor.
- No slide 14, resumir em uma frase: "as fontes medem públicos diferentes, então a conclusão é exploratória".

Com esses cortes, a apresentação cai para cerca de 12 minutos.

## Perguntas prováveis do professor ou dos colegas

### 1. Por que usar três fontes diferentes?

Resposta curta:

```text
Porque cada fonte mostra o fenômeno por um ângulo diferente. O Stack Overflow é a base principal para desenvolvedores. O StatCounter dá contexto do desktop geral. A Steam é uma fonte complementar para observar o público gamer e o possível papel do SteamOS. A gente não trata as três como iguais; compara principalmente a direção da tendência.
```

### 2. Vocês já treinaram modelo de Machine Learning?

Resposta curta:

```text
Ainda não. Esta etapa é exploratória e de proposta. Pelo CRISP-DM, primeiro estamos entendendo o problema, as fontes e a preparação dos dados. Modelagem fica como etapa futura se surgir uma pergunta adequada para prever ou classificar alguma coisa.
```

### 3. O resultado sobre Linux já é uma conclusão definitiva?

Resposta curta:

```text
Não. É um resultado exploratório. Ele mostra uma tendência interessante nos dados analisados, mas ainda precisa de avaliação mais profunda, recortes por perfil, país e discussão das limitações de cada fonte.
```

### 4. Por que a limpeza foi tão importante?

Resposta curta:

```text
Porque parte das respostas Linux aparecia em categorias como Other Linux-based, Linux non-WSL, Red Hat, NixOS e Pop!_OS. Se isso ficasse em Other, a leitura da tendência poderia ser distorcida. Por isso a preparação inicial reclassificou 26.268 seleções para a família Linux.
```

### 5. O Brasil é outra base?

Resposta curta:

```text
Não. Brasil é um recorte dentro do próprio Stack Overflow, filtrando a coluna Country. Ele é útil para comparar com o global, mas precisa de cuidado porque a amostra brasileira é menor, principalmente em 2025.
```

## Perguntas boas para fazer aos colegas

Use uma ou duas, dependendo do projeto apresentado:

```text
Qual etapa do CRISP-DM vocês acham que vai exigir mais esforço no projeto de vocês?
```

```text
Como vocês vão validar se os dados coletados realmente representam o problema que querem responder?
```

```text
Se os dados vierem com valores ausentes, duplicados ou categorias inconsistentes, qual estratégia de limpeza vocês pretendem usar?
```

```text
Vocês pretendem fazer análise exploratória primeiro ou já partir para modelagem? Por quê?
```
