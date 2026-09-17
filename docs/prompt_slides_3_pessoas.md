# Prompt para gerar slides da apresentacao

Copie e cole o texto abaixo no ChatGPT/Gamma/Canva para gerar os slides.

```text
Quero criar uma apresentacao de 10 minutos para um seminario de Mineracao de Dados.

IMPORTANTE:
- A apresentacao sera feita por 3 pessoas.
- O foco e proposta de projeto + analise exploratoria inicial.
- Nao diga que provamos causalidade.
- Nao invente dados.
- Use todos os bancos: Stack Overflow, StatCounter e Steam.
- Inclua o recorte Brasil, deixando claro que ele vem do Stack Overflow, nao de outra base.

Tema:
Adocao de sistemas operacionais entre desenvolvedores, mercado desktop geral e usuarios da Steam.

Pergunta de pesquisa:
Como a adocao de Windows, Linux e macOS evoluiu entre desenvolvedores de 2022 a 2025, e essa tendencia aparece tambem no mercado desktop geral e em usuarios da Steam?

Mensagem principal:
O projeto mostrou que trabalhar com dados reais exige entender fonte, schema e limpeza. A mudanca mais interessante encontrada foi o crescimento de Linux, mas o principal aprendizado foi que preparacao de dados e metodologia da fonte mudam a interpretacao.

Fontes de dados:
1. Stack Overflow Developer Survey
Link: https://github.com/StackExchange/Survey
Uso: fonte principal, respondentes da comunidade de desenvolvimento.
Dados usados: CSVs anuais de 2022, 2023, 2024 e 2025.

2. StatCounter Desktop OS Market Share
Link: https://gs.statcounter.com/os-market-share/desktop/worldwide
Uso: comparacao com mercado desktop geral.
Dados usados: market share mensal de sistemas operacionais desktop.

3. Steam Hardware & Software Survey
Link oficial: https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam
Historico em CSV: https://github.com/jdegene/steamHWsurvey
Uso: fonte complementar para usuarios da Steam/gamers.

Tamanho dos dados:
- Stack Overflow 2022: 108.83 MB
- Stack Overflow 2023: 158.63 MB
- Stack Overflow 2024: 159.53 MB
- Stack Overflow 2025: 140.89 MB
- Total Stack Overflow: 567.88 MB
- StatCounter: 0.04 MB
- Steam shs.csv: 4.10 MB
- Steam shs_platform.csv: 26.99 MB
- Total Steam: 31.09 MB

Metodologia:
Use CRISP-DM.

Mapeamento CRISP-DM:
- Business Understanding: entender diferencas de adocao de sistemas operacionais entre desenvolvedores, desktop geral e gamers.
- Data Understanding: estudar fontes, schemas, tamanhos, anos disponiveis e limitacoes.
- Data Preparation: baixar CSVs, validar arquivos, mapear colunas reais, tratar respostas multi-select, normalizar nomes dos sistemas e gerar tabelas analiticas.
- Modeling: nesta fase nao e prioridade; o foco e analise exploratoria.
- Evaluation: validar dados, testar normalizacao, comparar fontes e revisar limitacoes.
- Deployment: futuramente pode virar dashboard, API ou analise mais aprofundada.

Estrutura inicial dos dados:
Stack Overflow:
- CSV anual por ano.
- Cada ano pode ter colunas diferentes.
- Campos usados: id do respondente, pais, sistema operacional, emprego/perfil, experiencia.
- Respostas de sistema operacional podem ser multi-select.

StatCounter:
- CSV mensal.
- Campos: data, sistema operacional, market share, regiao/fonte.

Steam:
- CSV historico.
- Campos: data, plataforma, categoria, nome do sistema/versao, percentual.

Maior esforco / tecnicas importantes:
- Mapear schemas diferentes entre anos.
- Validar que os CSVs eram reais.
- Tratar respostas multi-select.
- Normalizar nomes diferentes para familias comparaveis: Windows, Linux, macOS etc.
- Comparar fontes que medem publicos diferentes.
- Evitar afirmar causalidade.

Descoberta exploratoria importante:
Na primeira leitura, Linux parecia menor porque algumas respostas claramente Linux estavam classificadas como Other.

Valores reclassificados para Linux:
- 2023: Other Linux-based, 6.712 selecoes
- 2023: Red Hat, 4.043 selecoes
- 2024: Other Linux-based, 4.697 selecoes
- 2024: Red Hat, 2.858 selecoes
- 2025: Linux (non-WSL), 5.261 selecoes
- 2025: Red Hat, 1.789 selecoes
- 2025: NixOS, 570 selecoes
- 2025: Pop!_OS, 338 selecoes
Total reclassificado: 26.268 selecoes.

Resultado Stack Overflow global:
Ano | Windows | Linux | macOS
2022 | 55.99% | 43.54% | 36.00%
2023 | 54.52% | 45.69% | 36.63%
2024 | 55.43% | 47.51% | 35.16%
2025 | 56.14% | 50.72% | 35.96%

Conclusao Stack Overflow:
Linux cresceu de 43.54% em 2022 para 50.72% em 2025, aumento de +7.17 pontos percentuais.

Recorte Brasil:
O dado do Brasil vem da propria base Stack Overflow Developer Survey. Ele foi obtido filtrando o campo Country para Brazil/Brasil. Nao e uma base externa.

Ano | n Brasil | Windows | Linux | macOS
2022 | 2.003 | 54.07% | 50.82% | 28.76%
2023 | 1.878 | 52.82% | 52.13% | 27.96%
2024 | 1.257 | 55.77% | 54.42% | 26.17%
2025 | 655 | 52.98% | 54.20% | 32.52%

Interpretacao do Brasil:
Linux aparece forte no recorte brasileiro, mas a amostra e menor. Usar como complemento, nao como conclusao principal.

Resultado StatCounter:
Ano | Windows | Linux | macOS
2022 | 79.05% | 2.69% | 7.93%
2023 | 73.18% | 3.24% | 9.98%
2024 | 77.34% | 4.38% | 8.03%
2025 | 77.76% | 4.16% | 8.19%

Conclusao StatCounter:
Linux tambem cresceu no desktop geral, de 2.69% para 4.16%.

Resultado Steam:
Ano | Windows | Linux | macOS
2022 | 96.14% | 1.38% | 2.45%
2023 | 96.41% | 1.94% | 1.62%
2024 | 96.33% | 2.05% | 1.40%
2025 | 94.23% | 3.57% | 2.19%

Conclusao Steam:
Linux cresceu entre usuarios da Steam de 1.38% para 3.57%.
SteamOS Holo esta contado dentro de Linux.
Em 2025, Linux e 3.57% do total da Steam. Dentro dos usuarios Linux, SteamOS Holo representa 26.32%, o que equivale a cerca de 0.94% do total da Steam.

Limitacoes:
- Stack Overflow representa respondentes desenvolvedores, nao todos os usuarios.
- StatCounter mede participacao por page views, nao pessoas individuais.
- Steam mede usuarios da Steam que participam da pesquisa, nao todos os gamers.
- As fontes tem metodologias diferentes.
- Respostas multi-select podem fazer percentuais somarem mais de 100%.
- Nao estamos provando causalidade.

Imagens que vou anexar e quero que sejam usadas:
1. reports/figures/06_trend_investigation.png
   Uso: resultado principal do Stack Overflow.
2. reports/figures/04_stackoverflow_vs_statcounter.png
   Uso: comparacao Stack Overflow vs StatCounter.
3. reports/figures/07_steam_linux_trend.png
   Uso: tendencia Linux na Steam.
4. reports/figures/03_brazil_vs_global_stackoverflow.png
   Uso: recorte Brasil vs global, se couber.

Quero uma apresentacao de 9 ou 10 slides.

Distribuicao obrigatoria para 3 pessoas e 10 minutos:

Pessoa 1: cerca de 3 minutos
- tema;
- pergunta de pesquisa;
- fontes;
- tamanho dos dados;
- explicar que Brasil vem do Stack Overflow.

Pessoa 2: cerca de 3 minutos
- CRISP-DM;
- estrutura dos dados;
- problemas de schema;
- respostas multi-select;
- limpeza e normalizacao;
- valores reclassificados de Other para Linux.

Pessoa 3: cerca de 4 minutos
- resultados Stack Overflow;
- recorte Brasil;
- comparacao StatCounter;
- comparacao Steam;
- limitacoes;
- conclusao e proximos passos.

Quero que voce gere:
1. Titulos dos slides.
2. Texto curto para cada slide.
3. Qual imagem usar em cada slide.
4. Fala pronta para cada uma das 3 pessoas.
5. Uma conclusao final forte, academica e simples.

Tom:
Academico simples, claro, sem exagerar. A apresentacao deve parecer uma proposta bem estruturada com analise exploratoria inicial, nao uma conclusao final definitiva.
```
