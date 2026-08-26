# CRISP-DM

## Business Understanding

Pergunta principal:

**Como a adocao dos principais sistemas operacionais difere entre desenvolvedores e mercado geral e como essa adocao evoluiu ao longo do tempo?**

O objetivo e comparar Windows, Linux, macOS, Ubuntu quando identificado separadamente e outros sistemas operacionais presentes nos dados, considerando perfil dos respondentes, pais, experiencia, licenciamento e custo quando houver fonte confiavel.

## Data Understanding

A fonte principal e o Stack Overflow Developer Survey, com anos 2022 a 2025. Cada ano pode ter schema diferente, portanto os cabecalhos sao inspecionados antes de qualquer transformacao.

StatCounter e usado como fonte secundaria de market share geral de sistemas operacionais desktop. A coleta usa a exportacao CSV oficial da pagina `https://gs.statcounter.com/os-market-share/desktop/worldwide`, em granularidade mensal desde 2022-01 ate o mes mais recente identificado na pagina.

A metrica do StatCounter nao representa respondentes do Stack Overflow nem numero absoluto de pessoas. Ela e uma participacao observada segundo a metodologia da fonte.

Precos e licenciamento sao mantidos em CSV separado, com fontes oficiais e data de coleta. Preco de software e exigencia/custo de hardware sao tratados como variaveis diferentes.

## Data Preparation

Etapas previstas:

- baixar dados reais com Git LFS;
- validar que os CSVs nao sao ponteiros LFS;
- calcular tamanho e SHA-256;
- inspecionar schemas por ano;
- mapear colunas reais para campos padronizados;
- tratar respostas multi-select;
- normalizar sistemas operacionais com regras explicitas;
- gerar tabelas analiticas separadas;
- salvar Parquet com compressao ZSTD;
- construir banco DuckDB para consultas.
- importar StatCounter em formato longo preservando o nome original do sistema;
- importar precos/licenciamento com preco de software, moeda, modelo de suporte e exigencia de hardware.

## Modeling

A prioridade e EDA e analise descritiva. Machine Learning so deve ser usado se houver pergunta justificavel, baseline, separacao treino/teste, cuidado com vazamento de dados e metricas adequadas.

Se os dados nao sustentarem um modelo serio, a decisao correta e documentar:

```text
Machine Learning nao foi utilizado porque nao agregaria resposta confiavel a pergunta de pesquisa.
```

## Evaluation

A avaliacao inclui:

- validacao de arquivos brutos;
- hashes e tamanhos reais;
- comparacao de schemas;
- testes de normalizacao;
- checagem de duplicidade de identificadores dentro de cada ano;
- consulta DuckDB sobre tabelas finais;
- validacao de datas e intervalo de market share;
- validacao de precos nao negativos, moedas e fontes;
- revisao das limitacoes metodologicas.

## Deployment

Entrega minima:

- notebooks reproduziveis;
- scripts de pipeline;
- banco DuckDB local;
- Parquet particionado por ano;
- README com instalacao, execucao e limitacoes.

Dashboard ou API so devem ser considerados depois de toda a pipeline funcionar.
