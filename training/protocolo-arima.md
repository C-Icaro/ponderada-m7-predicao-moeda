# Comparação exploratória ARIMA

Protocolo registrado antes dos ajustes ARIMA. O teste de Prophet já foi visto; esta etapa é exploratória e não transforma esse período em um novo teste intocado. O backend continua usando o artefato Prophet recomendado pelo professor.

Reutilizar os dois CSVs, sua conferência de hashes e datas e os cortes do [experimento Prophet](protocolo.md): validação de 08/04/2026 a 06/07/2026 e teste de 07/07/2026 a 04/10/2026. Prever cada bloco de 90 dias de uma vez, sem atualizar com preços observados durante o bloco. Usar MAE em USD para seleção, acompanhando RMSE e sMAPE.

1. Avaliar, nas janelas de três e aproximadamente 12 anos, as ordens fixadas previamente: `(0,1,0)`, `(1,1,0)`, `(0,1,1)` e `(1,1,1)`. Não usar sazonalidade nem tendência/drift. Dividir os preços por 1.000 para o ajuste numérico e multiplicar as previsões por 1.000 antes de calcular métricas.
2. Ajustar por máxima verossimilhança, com no máximo 200 iterações, exigindo estacionariedade e invertibilidade dos componentes. Registrar avisos e convergência. Excluir candidatos que falhem, não convirjam ou produzam valores não finitos.
3. Escolher a ordem por MAE de validação em cada janela. Diferenças até US$ 0,000001 são empate: preferir menor `p+q`, depois menor `p`, depois menor `q`. Escolher a janela também pela validação; empate na mesma tolerância favorece três anos. Salvar a decisão antes de avaliar o teste.
4. Reajustar a ordem escolhida para cada janela até 06/07/2026 e comparar as duas no teste, junto do Prophet já medido e da referência que repete o último preço conhecido. Não mudar ordens nem janela a partir do teste.
5. Exportar parâmetros e série de treino em JSON separado, reconstruir o estado com `ARIMA.filter` e conferir as previsões. Reajustar a janela ARIMA escolhida até 04/10/2026 e exportar `models/arima.json`, sem substituir `models/modelo.json`. O último ajuste não possui avaliação independente.

`ARIMA(0,1,0)` sem drift equivale à referência de último preço conhecido. A presença desse candidato torna visível quando modelos mais complexos não acrescentam valor. Uma janela de validação e teste limita a conclusão, e o erro de 90 dias não mede uma estratégia atualizada diariamente.

Fontes: [ARIMA no statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html), [ajuste](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.fit.html) e [reconstrução pelos parâmetros](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.filter.html).
