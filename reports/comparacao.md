# Comparação executada: três anos e histórico longo

BTC-USD diário, fechamento em USD por BTC. Mesma configuração Prophet e semente 42.

## Protocolo e resultado

A validação vai de 08/04/2026 a 06/07/2026. O teste final vai de 07/07/2026 a 04/10/2026. Cada previsão cobre 90 dias a partir de um único corte, sem atualizações diárias.

| Janela | MAE validação (USD) | MAE teste (USD) | RMSE teste (USD) | sMAPE teste |
| --- | ---: | ---: | ---: | ---: |
| 3 anos | 16.901,33 | 16.347,51 | 21.582,53 | 25,06% |
| Histórico longo, aproximadamente 12 anos | 43.627,86 | 28.836,89 | 29.900,36 | 33,77% |
| Repetir último preço conhecido | 6.613,45 | 8.707,09 | 11.875,25 | 12,09% |

A janela selecionada exclusivamente pelo MAE de validação foi **3y**. Essa decisão foi gravada antes do cálculo do teste e não foi alterada pelo resultado final.

No teste, o MAE da janela longa foi 76,40% maior que o da janela de três anos.

A referência simples teve MAE de teste menor que os dois Prophet. Este experimento não comprova vantagem de predição sobre repetir o último preço conhecido.

![Previsões e preços observados no teste](comparacao-teste.png)

## Artefatos e limites

Os modelos avaliados são `models/modelo-3y.json` e `models/modelo-12y.json`, ajustados até 06/07/2026. Os dois passaram pela verificação de previsão após exportar e recarregar JSON.

`models/modelo.json` foi reajustado usando a janela 3y e dados até 04/10/2026. Esse ajuste final é destinado à futura integração e ainda não tem avaliação independente. Os modelos gerados e CSVs de predições ficam fora do Git; a reprodução está no código e no notebook.

Uma única validação e um único teste não demonstram desempenho geral ou futuro. Não foram ajustados hiperparâmetros após observar o teste. Os intervalos de incerteza foram desabilitados.

[Protocolo anterior à execução](../training/protocolo.md) · [Resultados completos e hashes](comparacao.json) · [Escolha registrada na validação](selecao-validacao.json)
