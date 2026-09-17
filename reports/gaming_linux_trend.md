# Tendencia Linux entre gamers

## Fonte

A fonte gamer escolhida foi a Steam Hardware & Software Survey, pesquisa mensal oficial da Valve/Steam:

```text
https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam
```

Para ter historico em CSV, foi usado o repositorio publico `jdegene/steamHWsurvey`, que organiza dados da Steam Hardware Survey e dados antigos via Web Archive:

```text
https://github.com/jdegene/steamHWsurvey
```

Arquivos CSV consultados:

- `shs.csv`: 4.10 MB
- `shs_platform.csv`: 26.99 MB

## Metodo

A Steam mostra versoes especificas de sistema operacional na pagina geral, mas parte das versoes pode ficar escondida em `Other` ou nao aparecer no resumo principal. Por isso, esta verificacao nao soma apenas as versoes visiveis.

O calculo cruza as versoes visiveis no CSV geral com a pagina especifica de cada plataforma. Exemplo: se as distros Linux visiveis no resumo representam uma parte conhecida dentro da pagina Linux, essa proporcao e usada para estimar o total Linux.

## Resultado principal

Linux entre usuarios da Steam aumentou no periodo analisado:

- 2022-12: 1.38%
- 2025-12: 3.57%
- variacao: +2.19 p.p.
- crescimento relativo: 2.58x

Esse resultado combina com a tendencia corrigida do Stack Overflow: em outro publico, tambem aparece crescimento de Linux. A comparacao deve ser usada como evidencia complementar, nao como prova de causalidade.

## SteamOS entra onde?

SteamOS Holo entra dentro da familia Linux. O percentual de Linux parece pequeno porque ele e calculado sobre todos os usuarios da Steam, incluindo Windows e macOS. Dentro do subconjunto de usuarios Linux, SteamOS Holo aparece como uma das principais versoes.

Ano | Linux no total da Steam | SteamOS Holo dentro dos usuarios Linux | SteamOS Holo estimado no total da Steam
--- | --- | --- | ---
2022 | 1.38% | 24.07% | 0.33%
2023 | 1.94% | 40.53% | 0.79%
2024 | 2.05% | 35.59% | 0.73%
2025 | 3.57% | 26.32% | 0.94%

Interpretacao: em 2025, Linux representa 3.57% do total da Steam. Dentro desse grupo Linux, SteamOS Holo representa 26.32%. Por isso, SteamOS e contado, mas ele nao aparece como 26.32% do total da Steam; aparece como cerca de 0.94% do total.

## Dezembro de cada ano

Ano | Windows | Linux | macOS
--- | --- | --- | ---
2022 | 96.14% | 1.38% | 2.45%
2023 | 96.41% | 1.94% | 1.62%
2024 | 96.33% | 2.05% | 1.40%
2025 | 94.23% | 3.57% | 2.19%

## Ultimo mes disponivel no historico

- Mes: 2026-08
- Linux: 3.89%

## Interpretacao para o seminario

A conclusao que podemos defender e: depois da correcao da normalizacao, Linux cresceu no Stack Overflow; e uma fonte externa de gamers, a Steam Hardware Survey, tambem mostra crescimento de Linux entre usuarios da Steam.

Isso fortalece a pergunta de pesquisa porque mostra que a alta nao apareceu apenas dentro da nossa base principal. Mesmo assim, cada fonte mede um publico diferente:

- Stack Overflow: respondentes desenvolvedores.
- StatCounter: uso desktop observado em page views.
- Steam: usuarios da Steam que participam da pesquisa de hardware/software.

## Limitacoes

- A Steam Survey e opcional e anonima.
- Os dados historicos em CSV vem de um repositorio publico que organiza dados da Steam e Web Archive; a fonte oficial principal e a pagina da Steam.
- Usuarios da Steam nao representam todos os gamers nem todos os usuarios de desktop.
- Os percentuais sao de participacao, nao quantidade absoluta de pessoas.
- Comparar Steam com Stack Overflow e StatCounter serve para contexto, nao para causalidade.

Gerado em 2026-09-13.
