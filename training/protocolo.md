# Protocolo definido antes do treinamento

Comparar o mesmo Prophet com dois históricos diários de BTC-USD: três anos (05/10/2023 a 04/10/2026) e todo o histórico disponível no Yahoo (17/09/2014 a 04/10/2026, aproximadamente 12 anos). Os preços nas datas comuns devem coincidir. Não interpolar preços nem embaralhar datas.

1. Ajustar primeiro a janela de três anos e depois a longa, usando apenas datas anteriores a 08/04/2026. Prever de uma vez os 90 dias de 08/04/2026 a 06/07/2026, a validação.
2. Escolher a janela pelo menor MAE da validação. Em empate exato, escolher três anos. Registrar essa decisão antes de calcular resultados do teste.
3. Reajustar as duas versões com dados até 06/07/2026 e prever de uma vez os mesmos 90 dias, de 07/07/2026 a 04/10/2026. Esse é o teste final reservado. Mostrar os dois resultados sem alterar a escolha feita pela validação.
4. Comparar também com uma referência simples que repete, pelos 90 dias, o último fechamento conhecido no respectivo corte.
5. Exportar os dois modelos avaliados em JSON. Recarregar cada JSON e verificar que reproduz suas previsões. Reajustar a janela escolhida com todos os dados disponíveis até 04/10/2026 e exportar `models/modelo.json` para a futura integração. Esse último ajuste ainda não terá avaliação independente.

Configuração igual para ambos: tendência linear, sazonalidades anual e semanal habilitadas, diária desabilitada, 25 pontos potenciais de mudança, `changepoint_range=0.8`, `changepoint_prior_scale=0.05`, sazonalidade aditiva com `seasonality_prior_scale=10`, `mcmc_samples=0`, `uncertainty_samples=0` e semente de ajuste 42. Não haverá busca de hiperparâmetros nem intervalos de incerteza neste experimento.

Métricas: MAE (média dos erros absolutos, USD por BTC), RMSE (raiz da média dos erros ao quadrado, mesma unidade) e sMAPE (média de `200 * |y - yhat| / (|y| + |yhat|)`, em porcentagem; se ambos forem zero, contribuição zero). MAE é o único critério de seleção definido antecipadamente.

A avaliação mede previsões de até 90 dias a partir de um corte fixo. Não representa previsões diárias de amanhã com atualização do modelo, nem prova desempenho em outros períodos. Uma única janela de validação e teste limita a generalização.

Fontes técnicas: [Quick Start](https://facebook.github.io/prophet/docs/quick_start.html), [avaliação temporal](https://facebook.github.io/prophet/docs/diagnostics.html) e [serialização JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).
