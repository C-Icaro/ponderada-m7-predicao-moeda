# Dados

## Recorte obtido em 05/10/2026

| Campo | Valor observado |
| --- | --- |
| Fonte | [Yahoo Finance, histórico BTC-USD](https://finance.yahoo.com/quote/BTC-USD/history/) |
| Par e unidade | BTC-USD, fechamento em USD por BTC |
| Frequência e referência temporal | Diária, UTC conforme os metadados da fonte |
| Período incluído | 05/10/2023 a 04/10/2026, três anos |
| Quantidade | 1.096 registros, além do cabeçalho |
| CSV local | `data/processed/btc_usd_daily.csv` |
| Colunas | `ds`: data YYYY-MM-DD sem timezone; `y`: `Close` numérico, não ajustado |
| Tamanho medido | 26.968 bytes, aproximadamente 26,3 KiB |
| Validação | Série diária completa, sem duplicatas, lacunas ou fechamentos inválidos |

O [registro de procedência](coleta-btc-usd.json) contém URL de obtenção, horário UTC da coleta, intervalo, filtros, tamanho e SHA-256 do CSV. O dia 05/10/2026 retornado adicionalmente pelo Yahoo foi excluído, pois ainda estava em andamento. Nenhum preço foi interpolado ou preenchido.

Uma observação por dia é suficiente para a primeira demonstração proposta com Prophet. Não precisamos armazenar negociações individuais ou dados por minuto. O arquivo está no contrato `ds`/`y` do [Quick Start oficial](https://facebook.github.io/prophet/docs/quick_start.html); o modelo ainda não foi treinado.

## Obtenção pelo terminal

Na raiz do repositório, com Python e conexão à internet:

```powershell
python data/download_btc.py
```

O [script do projeto](download_btc.py) usa apenas a biblioteca padrão do Python para consultar o endpoint de histórico do Yahoo. Não foi necessário instalar `yfinance` ou Prophet para esta coleta. Ele grava o CSV local e atualiza os metadados de procedência. Se encontrar lacunas, duplicatas, valores inválidos ou erro de rede, interrompe a coleta, sem preencher dados.

As datas padrão são fixas para este experimento. Para alterar o recorte:

```powershell
python data/download_btc.py --start 2023-10-05 --end 2026-10-05
```

O início é inclusivo e o fim exclusivo. O script também filtra explicitamente o intervalo, porque a fonte pode retornar uma linha adicional. Uma nova obtenção pode trazer revisões dos preços pela fonte; compare o hash e os metadados para identificar mudanças.

### Alternativa com yfinance

Quando o ambiente de treinamento for preparado, também é possível usar `yfinance`. Os parâmetros equivalentes são `tickers="BTC-USD"`, `start="2023-10-05"`, `end="2026-10-05"`, `interval="1d"` e `auto_adjust=False`, selecionando somente data e `Close`. A biblioteca documenta o fim exclusivo e o ajuste automático como padrão, por isso esses parâmetros precisam ser explícitos. [Referência oficial do projeto yfinance](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html).

## Espaço, uso e limites

A inspeção encontrou aproximadamente 2,81 GiB livres em C: durante a coleta. O CSV ocupa uma parcela mínima desse espaço. O consumo do ambiente Python, caches e imagens Docker ainda precisa ser medido antes de instalar dependências ou construir containers.

Os arquivos em `data/raw/` e `data/processed/` continuam fora do Git. O repositório publica o script e a procedência para reproduzir a obtenção. A licença de redistribuição dos preços não foi confirmada neste checkpoint; a [documentação do yfinance](https://ranaroussi.github.io/yfinance/) orienta consultar as condições do Yahoo e descreve uso pessoal da API. A obtenção depende da internet e da disponibilidade da fonte.

O autor pediu pelo menos três anos, e o recorte foi ampliado após a primeira coleta de dois anos. Para avaliação, a proposta inicial é reservar os últimos 90 dias (07/07/2026 a 04/10/2026) e treinar com os 1.006 anteriores. Essa divisão ainda não foi executada em um modelo e não demonstra precisão preditiva.
