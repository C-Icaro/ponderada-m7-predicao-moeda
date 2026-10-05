# Dados

Os dois CSVs de BTC-USD em `data/processed/` estão versionados no repositório. São preços públicos de mercado obtidos do Yahoo Finance, sem dados pessoais. Para reproduzir o treinamento, use os arquivos incluídos no clone; uma nova coleta é opcional. O [roteiro principal](../README.md) executa treinamento, API e cliente em Docker.

## Recortes obtidos em 05/10/2026

| Campo | Valor observado |
| --- | --- |
| Fonte | [Yahoo Finance, histórico BTC-USD](https://finance.yahoo.com/quote/BTC-USD/history/) |
| Par e unidade | BTC-USD, fechamento em USD por BTC |
| Frequência e referência temporal | Diária, UTC conforme os metadados da fonte |
| Colunas | `ds`: data YYYY-MM-DD sem timezone; `y`: `Close` numérico, não ajustado |
| Validação | Série diária completa, sem duplicatas, lacunas ou fechamentos inválidos |

| Recorte | Período incluído | Registros | Tamanho medido | CSV versionado | Procedência |
| --- | --- | ---: | ---: | --- | --- |
| Primeira versão, três anos | 05/10/2023 a 04/10/2026 | 1.096 | 26.968 bytes, 26,3 KiB | `data/processed/btc_usd_daily.csv` | [Metadados de três anos](coleta-btc-usd.json) |
| Comparação, histórico disponível de aproximadamente 12 anos | 17/09/2014 a 04/10/2026 | 4.401 | 116.370 bytes, 113,6 KiB | `data/processed/btc_usd_daily_12y.csv` | [Metadados de 12 anos](coleta-btc-usd-12y.json) |

Os registros de procedência contêm URL de obtenção, horário UTC da coleta, intervalo, filtros, tamanho e SHA-256 de cada CSV. O dia 05/10/2026 retornado adicionalmente pelo Yahoo foi excluído, pois ainda estava em andamento. Nenhum preço foi interpolado ou preenchido. O histórico de 12 anos corresponde ao período disponível nessa fonte, não a todas as negociações de Bitcoin desde sua criação.

O CSV de três anos foi preservado. Seus 1.096 fechamentos são exatamente iguais aos valores das mesmas datas no CSV de 12 anos. Assim, a comparação entre modelos pode variar o tamanho do histórico sem mudar os preços nas datas comuns. O SHA-256 preservado do CSV de três anos é `efcfb47437769e79c12171752abf717ac84af17535d98ebfef82f066f278e4f6`; o do CSV de 12 anos é `1ee1459f8acf0d4a9ffc2aba779a0f856783f9a64ecb9d330845ecb4a21902ee`.

Uma observação por dia é suficiente para a demonstração proposta com Prophet. Não precisamos armazenar negociações individuais ou dados por minuto. Ambos os arquivos seguem o contrato `ds`/`y` do [Quick Start oficial](https://facebook.github.io/prophet/docs/quick_start.html). A execução e a avaliação dos modelos são documentadas em [training](../training/README.md).

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

Para obter o histórico de 12 anos em arquivos separados, sem sobrescrever o CSV e a procedência de três anos:

```powershell
python data/download_btc.py --start 2014-09-17 --end 2026-10-05 --output data/processed/btc_usd_daily_12y.csv --metadata data/coleta-btc-usd-12y.json
```

Os caminhos opcionais `--output` e `--metadata` são relativos ao diretório de execução. Se forem omitidos, os destinos continuam sendo os arquivos da primeira versão de três anos.

O início é inclusivo e o fim exclusivo. O script também filtra explicitamente o intervalo, porque a fonte pode retornar uma linha adicional. Uma nova obtenção pode trazer revisões dos preços pela fonte; compare o hash e os metadados para identificar mudanças.

### Alternativa com yfinance

Quando o ambiente de treinamento for preparado, também é possível usar `yfinance`. Os parâmetros equivalentes são `tickers="BTC-USD"`, `start="2023-10-05"`, `end="2026-10-05"`, `interval="1d"` e `auto_adjust=False`, selecionando somente data e `Close`. A biblioteca documenta o fim exclusivo e o ajuste automático como padrão, por isso esses parâmetros precisam ser explícitos. [Referência oficial do projeto yfinance](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html).

## Espaço, uso e limites

A inspeção encontrou aproximadamente 2,81 GiB livres em C: durante a coleta. Depois da instalação e do treinamento, a pasta `.venv` tinha aproximadamente 65,3 MiB de arquivos e havia cerca de 2,72 GiB livres em C:. Esse ambiente reutiliza pandas, NumPy e Matplotlib já instalados por meio de `--system-site-packages`; uma instalação independente poderá ocupar mais espaço. O consumo de imagens Docker ainda precisa ser medido.

O repositório inclui os dois CSVs descritos acima, o script de coleta e os metadados de procedência. Outros arquivos em `data/raw/` e `data/processed/` continuam ignorados pelo Git. Uma nova coleta depende da internet e da disponibilidade do Yahoo; pode substituir os CSVs e seus metadados. Preserve a cópia versionada para reproduzir exatamente os dados deste experimento.

O autor pediu pelo menos três anos, e o recorte foi ampliado após a primeira coleta de dois anos. Depois, pediu confrontar a primeira versão com o histórico de 12 anos. A comparação foi executada com uma validação anterior ao teste: 08/04/2026 a 06/07/2026. No teste final reservado, de 07/07/2026 a 04/10/2026, os ajustes usam 1.006 observações de treino no recorte de três anos e 4.311 no longo. [Resultados medidos](../reports/comparacao.md). Ter mais observações, por si só, não demonstra precisão preditiva.
