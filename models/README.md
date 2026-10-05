# Artefatos Prophet

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

Na arquitetura proposta, o backend Python carregará `models/modelo.json` por um volume Docker somente leitura, em `/app/models/modelo.json`. A entrada terá datas `ds` e a saída terá previsões `yhat` em USD por BTC. Essa integração ainda não foi implementada. O artefato não fornece intervalos de incerteza, pois `uncertainty_samples=0` neste experimento.
