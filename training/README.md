# Treinamento e comparação

Primeira versão executada em 05/10/2026 com Python 3.13.13 e Prophet 1.5.0. O [script canônico](train_compare.py) e o [notebook com resultados](comparacao.ipynb) confrontam os históricos de três anos e aproximadamente 12 anos de BTC-USD. Os CSVs usam `ds` para data UTC sem timezone e `y` para fechamento em USD por BTC.

## Protocolo e resultado

O [protocolo definido antes do ajuste](protocolo.md) mantém a mesma configuração e semente 42 nos dois modelos. Não embaralha datas nem usa os preços da janela prevista durante o ajuste. Cada avaliação prevê um bloco de 90 dias a partir de um único corte.

| Etapa | Treino de três anos | Treino do histórico longo | Datas previstas |
| --- | --- | --- | --- |
| Validação | 916 dias, até 07/04/2026 | 4.221 dias, até 07/04/2026 | 08/04/2026 a 06/07/2026, 90 dias |
| Teste final | 1.006 dias, até 06/07/2026 | 4.311 dias, até 06/07/2026 | 07/07/2026 a 04/10/2026, 90 dias |

A regra escolhe o menor MAE na validação; empate exato favorece três anos. A [escolha registrada](../reports/selecao-validacao.json) foi `3y`, com MAE de validação de USD 16.901,33, contra USD 43.627,86 da janela longa. O resultado do teste não foi usado para alterar essa decisão.

| Previsão no teste final | MAE (USD) | RMSE (USD) | sMAPE |
| --- | ---: | ---: | ---: |
| Prophet, três anos | 16.347,51 | 21.582,53 | 25,06% |
| Prophet, histórico longo | 28.836,89 | 29.900,36 | 33,77% |
| Repetir o último fechamento conhecido | 8.707,09 | 11.875,25 | 12,09% |

MAE é a média dos erros absolutos. RMSE dá mais peso a erros grandes e mantém a unidade USD por BTC. sMAPE expressa o erro relativo em porcentagem. Menor é melhor para as três métricas.

Três anos tiveram menor erro que o histórico longo neste recorte. A referência simples teve menor erro que ambos os Prophet, portanto esta execução não demonstra vantagem preditiva sobre repetir o último preço conhecido. Consulte o [relatório e gráfico](../reports/comparacao.md) e os [resultados completos, ambiente e hashes](../reports/comparacao.json).

## Reprodução pelo terminal

Na raiz do repositório, obtenha os dois CSVs em destinos separados:

```powershell
python data/download_btc.py --start 2023-10-05 --end 2026-10-05
python data/download_btc.py --start 2014-09-17 --end 2026-10-05 --output data/processed/btc_usd_daily_12y.csv --metadata data/coleta-btc-usd-12y.json
```

Os CSVs locais ficam fora do Git. A [procedência dos dados](../data/README.md) documenta a fonte, os tamanhos e os hashes. Uma nova coleta pode receber revisões da fonte; nesse caso, resultados antigos não comprovam a avaliação dos novos preços.

Neste computador, já havia NumPy, pandas e Matplotlib instalados. A preparação abaixo reutiliza esses pacotes para economizar espaço, mantendo os requisitos explícitos:

```powershell
python -m venv --system-site-packages .venv
.venv\Scripts\python.exe -m pip install --no-cache-dir --only-binary=:all: -r requirements-training.txt
.venv\Scripts\python.exe training/train_compare.py
.venv\Scripts\python.exe -m unittest discover -s training -p "test_train_compare.py"
```

As versões usadas estão em [requirements-training.txt](../requirements-training.txt). Os testes verificam métricas, separação temporal, seleção e geração do relatório, sem ajustar modelos. O diretório `.venv` teve 68.455.566 bytes, aproximadamente 65,28 MiB, medidos neste ambiente com dependências compartilhadas. Esse tamanho não inclui os pacotes globais reaproveitados e pode ser diferente em outro computador. `.venv` não é versionado.

O notebook é uma apresentação opcional da mesma implementação. Para executá-lo, selecione um kernel Python com Prophet e IPython disponíveis. O treinamento pelo terminal dispensa interface de notebook e registro de kernel.

## Artefatos e limites

Os [modelos avaliados](../models/README.md), `modelo-3y.json` e `modelo-12y.json`, foram ajustados até 06/07/2026. Após a comparação, a janela escolhida foi reajustada com 1.096 observações até 04/10/2026 e exportada para `models/modelo.json`. Esse artefato final ainda não tem avaliação independente posterior a essa data.

Os modelos usam a serialização JSON nativa do Prophet; exportar e recarregar preservou as previsões verificadas. Modelos e CSVs de previsões são gerados localmente e ignorados pelo Git. Código, notebook, procedência e relatórios permitem reproduzir a execução; hashes identificam os artefatos medidos.

Foi usada uma única janela de validação e uma de teste. Não houve busca de hiperparâmetros depois de observar o teste; os intervalos de incerteza estão desabilitados. O resultado se refere à previsão em bloco de até 90 dias e não comprova comportamento em outros períodos. A integração de inferência é descrita em [backend](../backend/README.md).

## Experimento exploratório ARIMA

Após ver os resultados Prophet, o autor solicitou ARIMA. O [protocolo adicional](protocolo-arima.md) fixou quatro ordens sem drift e seus desempates antes dos ajustes. O [notebook executado](arima.ipynb) chama [train_arima.py](train_arima.py); ambos reutilizam datas, hashes, métricas e cortes do experimento anterior.

```powershell
.venv\Scripts\python.exe -m pip install --no-cache-dir --only-binary=:all: -r requirements-arima.txt
.venv\Scripts\python.exe training/train_arima.py
.venv\Scripts\python.exe -m unittest discover -s training -p "test_*.py"
```

Execute Prophet primeiro, pois ARIMA confere e reutiliza seus resultados e CSV de previsões. As dependências ARIMA são opcionais para o backend. Os oito candidatos de validação convergiram sem avisos; `(0,1,0)` venceu nas duas janelas. O empate favoreceu três anos. Seu MAE de teste, USD 8.707,09, é igual ao de repetir o último preço conhecido. Não houve ganho sobre essa referência. [Resultados, gráfico e limites](../reports/arima.md).

A etapa é exploratória porque o teste já havia sido observado. ARIMA gera JSONs separados, reconstruídos pelos parâmetros e série de treino, com diferença zero nas previsões conferidas. O ajuste final não possui avaliação independente e não substitui o Prophet servido pelo backend.

Referências oficiais: [Quick Start](https://facebook.github.io/prophet/docs/quick_start.html), [avaliação temporal](https://facebook.github.io/prophet/docs/diagnostics.html) e [serialização JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).
