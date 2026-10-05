# Treinamento

Reservado para um notebook de treinamento. Ainda não implementado.

Proposta mínima: ler um CSV pequeno, preparar `ds` (data) e `y` (preço numérico), ordenar a série, separar treino e teste cronologicamente e ajustar um modelo Prophet no treino.

Para avaliar, prever com `modelo.predict(teste[['ds']])` e comparar `yhat` com o preço observado nas mesmas datas. O recorte de teste fica fora do `fit`.

Exportar para `models/modelo.json` com `prophet.serialize.model_to_json`. Registrar fonte dos dados, horizonte, unidade da cotação, dependências e instruções para executar novamente o notebook.

Referências: [Quick Start](https://facebook.github.io/prophet/docs/quick_start.html) e [Saving models](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models). Este é o plano de implementação, sem notebook executado neste checkpoint.
