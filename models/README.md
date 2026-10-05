# Artefatos dos modelos

Três arquivos JSON foram gerados na execução de 05/10/2026. Eles usam `model_to_json` para exportar e `model_from_json` para carregar, seguindo a [documentação oficial do Prophet](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).

| Arquivo local | Histórico de treino | Final do treino | Tamanho medido | Avaliação |
| --- | --- | --- | ---: | --- |
| `modelo-3y.json` | Três anos, 1.006 observações anteriores ao teste | 06/07/2026 | 166.117 bytes | Teste de 07/07/2026 a 04/10/2026 |
| `modelo-12y.json` | Histórico longo, 4.311 observações anteriores ao teste | 06/07/2026 | 703.566 bytes | Mesmo teste de 90 dias |
| `modelo.json` | Janela escolhida de três anos, 1.096 observações | 04/10/2026 | 180.508 bytes | Reajuste final, sem avaliação independente posterior |

O [protocolo](../training/protocolo.md) selecionou a janela `3y` pelo menor MAE na validação de 08/04/2026 a 06/07/2026. No teste posterior, três anos também tiveram menor erro que o histórico longo. A referência que repete o último fechamento conhecido superou ambos os Prophet. Os [resultados reais](../reports/comparacao.md) não demonstram vantagem dos modelos sobre essa referência simples.

Os dois modelos avaliados e o artefato final passaram por exportação e recarga JSON: a maior diferença absoluta nas previsões verificadas foi `0.0`. Essa verificação preserva a serialização; ela não substitui a avaliação preditiva do reajuste final.

## Identificação dos arquivos

Hashes SHA-256 registrados em [reports/comparacao.json](../reports/comparacao.json):

| Arquivo | SHA-256 |
| --- | --- |
| `modelo-3y.json` | `ba08218862f6bbd72e5c7cd57adc49a8aa9fb82b0cc300a3df9fb14fc09b4c4e` |
| `modelo-12y.json` | `f1741f72c591c01a4ef3bcd78e99d64d73ec9ce78f94e1dc00cb2a340caf381f` |
| `modelo.json` | `8fcd04e80bd236a8a879be335a19acc80830b47d0e030aae3044fc0421a716c1` |

Esses hashes identificam os arquivos desta execução. Reexecutar com outro ambiente ou dados revisados pode gerar hashes diferentes.

## Reprodução e uso previsto

Os JSONs continuam ignorados pelo Git, conforme o contrato existente. Reproduza-os com o [script de treinamento](../training/train_compare.py), seguindo a [preparação do ambiente e coleta](../training/README.md). O [notebook executado](../training/comparacao.ipynb), os requisitos, a procedência e os relatórios documentam o experimento.

```powershell
.venv\Scripts\python.exe training/train_compare.py
```

O backend Python usa `models/modelo.json` por um volume Docker somente leitura, em `/app/models/modelo.json`. A entrada contém uma data `ds` e a saída contém `ds` e `yhat` em USD por BTC. Consulte a [execução do serviço](../backend/README.md). O artefato não fornece intervalos de incerteza, pois `uncertainty_samples=0` neste experimento.

## ARIMA exploratório

O [experimento adicional](../training/protocolo-arima.md) gerou `arima-3y.json`, `arima-12y.json` e `arima.json`, sem substituir o artefato Prophet. As ordens escolhidas na validação foram `(0,1,0)` nas duas janelas. Esse modelo equivale à referência do último fechamento conhecido e teve MAE de teste de USD 8.707,09 em ambas.

Os JSONs contêm ordem, escala, preços do treino e parâmetros. `ARIMA.filter` reconstrói o estado; a diferença máxima nas previsões conferidas foi zero. O ajuste final `arima.json` usa os 1.096 preços até 04/10/2026, mede 21.887 bytes e tem SHA-256 `d15f1d09ec262b0988a6a553b7688aac2edce168835ca777258126ef6eb8a65d`. Não tem avaliação independente posterior. [Demais hashes e métricas](../reports/arima.json).

Reprodução, depois do Prophet e da instalação dos [requisitos opcionais ARIMA](../requirements-arima.txt):

```powershell
.venv\Scripts\python.exe training/train_arima.py
```
