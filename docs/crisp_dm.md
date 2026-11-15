# CRISP-DM

## Business Understanding

Pergunta principal:

**Como a adocao dos principais sistemas operacionais difere entre desenvolvedores, mercado geral e uma fonte complementar de gamers, e como essa adocao evoluiu ao longo do tempo?**

O objetivo e comparar Windows, Linux, macOS, Ubuntu quando identificado separadamente e outros sistemas operacionais presentes nos dados, considerando ano, pais, perfil profissional e experiencia quando esses campos existirem nos schemas reais.

## Data Understanding

A fonte principal e o Stack Overflow Developer Survey, com anos 2022 a 2025. Cada ano pode ter schema diferente, portanto os cabecalhos sao inspecionados antes de qualquer transformacao.

StatCounter e usado como fonte secundaria de market share geral de sistemas operacionais desktop. A coleta usa a exportacao CSV oficial da pagina `https://gs.statcounter.com/os-market-share/desktop/worldwide`, em granularidade mensal desde 2022-01 ate o mes mais recente identificado na pagina.

A metrica do StatCounter nao representa respondentes do Stack Overflow nem numero absoluto de pessoas. Ela e uma participacao observada segundo a metodologia da fonte.

Steam Hardware & Software Survey e usada como fonte complementar para verificar se a tendencia de Linux tambem aparece entre usuarios da Steam/gamers. O historico em CSV vem de `https://github.com/jdegene/steamHWsurvey`, que organiza dados da pesquisa oficial da Steam e dados antigos via Web Archive.

Precos e licenciamento foram tratados como possibilidade de extensao futura. Para o seminario, as fontes principais sao Stack Overflow Developer Survey, StatCounter e a verificacao complementar Steam.

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
- construir banco DuckDB para consultas;
- importar StatCounter em formato longo preservando o nome original do sistema;
- calcular a tendencia complementar da Steam em relatorio separado;
- manter precos/licenciamento como extensao futura, caso a analise precise discutir custo.

## Modeling

A tarefa preditiva complementar e classificar se um respondente selecionou Linux com base nas variaveis de perfil do Stack Overflow (pais, idade, emprego e tipo de desenvolvedor). A coluna de experiencia profissional foi excluida: em 2025 ela usa `WorkExp`, enquanto os anos anteriores usam `YearsCodePro`, sem equivalencia direta. A classe positiva e Linux; as demais respostas validas sao a classe negativa. Respondentes sem resposta valida de sistema operacional ficam fora da modelagem.

O `src/train_model.py` compara um baseline de classe majoritaria, regressao logistica e arvore de decisao regularizada. Valores ausentes nos atributos sao preservados como uma categoria explicita durante a imputacao; atributos categoricos sao codificados com one-hot encoding. A proporcao de cada classe e registrada e nao se aplica reamostragem automatica.

Para evitar avaliar em observacoes do mesmo periodo de treino, o ano mais recente disponivel e reservado como teste temporal, e os anos anteriores formam o treino. O ano nao e usado como preditor. O relatorio inclui acuracia, acuracia balanceada, precisao, recall e F1 para Linux, alem de ROC-AUC quando as duas classes estao presentes no teste. O melhor modelo e selecionado por F1 Linux, com acuracia balanceada e ROC-AUC como desempate.

Os resultados sao associativos, nao causais. Surveys anuais independentes, mudancas de schema e diferencas de amostragem limitam a generalizacao. A execucao gera `reports/model_evaluation.md`, incluindo contagens de dados ausentes, balanceamento do alvo, comparacao dos modelos e matriz de confusao.

## Evaluation

A avaliacao inclui:

- validacao de arquivos brutos;
- hashes e tamanhos reais;
- comparacao de schemas;
- testes de normalizacao;
- checagem de duplicidade de identificadores dentro de cada ano;
- consulta DuckDB sobre tabelas finais;
- validacao de datas e intervalo de market share;
- comparacao da tendencia de Linux com a Steam Survey;
- avaliacao temporal do classificador contra o baseline;
- revisao das limitacoes metodologicas.

## Deployment

Entrega minima:

- notebooks reproduziveis;
- scripts de pipeline;
- banco DuckDB local;
- Parquet particionado por ano;
- README com instalacao, execucao e limitacoes.

Dashboard ou API so devem ser considerados depois de toda a pipeline funcionar.
