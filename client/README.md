# Cliente no terminal

O [cliente Python](terminal.py) usa apenas a biblioteca padrão. Ele faz duas requisições reais: consulta `GET /health` e envia `POST /predict` ao backend na porta **6767**. Não requer interface gráfica nem instalação de pacotes.

Inicie o [backend](../backend/README.md) e mantenha seu terminal aberto. Em um segundo terminal, na raiz do repositório:

```powershell
python client/terminal.py 2026-10-05
```

Para usar automaticamente o primeiro dia aceito, retornado por `/health`:

```powershell
python client/terminal.py
```

O endereço padrão é `http://127.0.0.1:6767`; `--url` permite informar outra URL para a mesma API. O script imprime o status HTTP e o JSON de cada resposta. Retorna código de saída 1 para erro HTTP ou falha de conexão, incluindo uma mensagem legível quando o servidor devolve texto em vez de JSON.

Na execução de 05/10/2026, a saúde e a previsão retornaram HTTP 200. Para `ds="2026-10-05"`, o container respondeu `yhat=78248.948192546`, em USD por BTC. A [evidência da jornada](../reports/integracao.json) registra requisição, resposta e identificação do artefato usado.

## PowerShell como cliente

As mesmas operações podem ser feitas diretamente pelo terminal:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:6767/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:6767/predict -ContentType 'application/json' -Body '{"ds":"2026-10-05"}'
```

No artefato atual, a API aceita somente datas de **05/10/2026 a 11/10/2026**, os sete dias após o fim do treino. Um exemplo de erro verificado:

```powershell
python client/terminal.py 2026-10-12
```

Essa chamada retorna HTTP 422, uma mensagem com o intervalo permitido e saída 1. Datas impossíveis, formatos diferentes de `YYYY-MM-DD`, campos extras e tipos incorretos também são rejeitados. O [contrato completo](../backend/README.md) detalha as respostas.

O cliente consulta um modelo já ajustado. As métricas de comparação dos históricos foram medidas em blocos de 90 dias; não representam uma avaliação independente deste reajuste final nem do horizonte de sete dias da API.
