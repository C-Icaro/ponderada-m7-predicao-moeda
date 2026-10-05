# Treinamento

Reservado para um notebook de treinamento. Ainda não implementado.

Proposta mínima: ler um CSV pequeno, preparar `ds` (data) e `y` (preço numérico), ordenar a série, separar treino e teste cronologicamente e ajustar um modelo Prophet no treino.

A [coleta de BTC-USD](../data/README.md) já forneceu `data/processed/btc_usd_daily.csv`, com 1.096 registros diários e 26,3 KiB, de 05/10/2023 a 04/10/2026. Corte inicial proposto: 1.006 registros para treino até 06/07/2026 e 90 para teste de 07/07/2026 a 04/10/2026. A unidade de `y` é USD por BTC; `ds` mantém a data UTC da fonte, sem timezone no CSV. O corte ainda não foi usado em treinamento.

Para avaliar, prever com `modelo.predict(teste[['ds']])` e comparar `yhat` com o preço observado nas mesmas datas. O recorte de teste fica fora do `fit`.

Exportar para `models/modelo.json` com `prophet.serialize.model_to_json`. Registrar fonte dos dados, horizonte, unidade da cotação, dependências e instruções para executar novamente o notebook.

Referências: [Quick Start](https://facebook.github.io/prophet/docs/quick_start.html) e [Saving models](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models). Este é o plano de implementação, sem notebook executado neste checkpoint.
