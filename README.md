# Ponderada M7: previsão de BTC-USD

Solução simples: dados CSV → treinamento Prophet → modelo JSON → API em Docker → cliente no terminal.

## Executar do zero

Pré-requisitos: Git, Docker com Compose e acesso ao repositório. A primeira construção da imagem usa internet para baixar a base Python e as dependências. Treinamento, API e cliente executam em containers, usando os dados incluídos no repo.

### 1. Clonar e entrar na pasta

Enquanto a entrega está em revisão, use a branch abaixo, que contém os arquivos de execução:

```sh
git clone --branch docs/arquitetura-inicial https://github.com/C-Icaro/ponderada-m7-predicao-moeda.git
cd ponderada-m7-predicao-moeda
```

Execute os próximos comandos na raiz dessa pasta, em um terminal com `docker` disponível.

No Windows deste projeto, o Docker está no WSL `Ubuntu-24.04`. Para abrir esse terminal na pasta do repo, execute no PowerShell:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD"
```

Siga os comandos Docker dentro do WSL e mantenha a sessão aberta enquanto a API estiver rodando. Com Docker Desktop disponível diretamente no PowerShell, essa etapa é dispensável.

### 2. Construir a imagem e treinar

```sh
docker compose build
docker run --rm --user 0:0 --mount "type=bind,source=${PWD},target=/workspace" --workdir /workspace ponderadacomp-backend:local python training/train_compare.py
```

O primeiro comando usa o [Dockerfile](Dockerfile) e instala as versões de [requirements-backend.txt](requirements-backend.txt), iguais às do treinamento Prophet. O segundo executa [training/train_compare.py](training/train_compare.py) em um container temporário: compara três e 12 anos, gera os relatórios em `reports/` e salva **`models/modelo.json`**, que a API precisa carregar.

A pasta do repo é montada no container, por isso os arquivos gerados permanecem no computador após ele terminar. `--user 0:0` permite gravar nessa pasta; a API executa como o usuário `app` definido no Dockerfile. Em Linux, os arquivos gerados pelo treinamento podem ficar com proprietário root. Os modelos gerados continuam fora do Git.

### 3. Iniciar a API

```sh
docker compose up --no-build
```

Mantenha esse terminal aberto. O [compose.yaml](compose.yaml) inicia o backend, monta `models/` somente para leitura e disponibiliza a API em **http://127.0.0.1:6767**, na rede Docker **`PonderadaComp`**. O modelo é carregado ao iniciar o serviço; depois de treinar novamente, reinicie a API.

### 4. Fazer uma previsão

Abra outro terminal com Docker disponível, entre na mesma pasta do repo e execute:

```sh
docker compose ps
docker run --rm --network PonderadaComp --mount "type=bind,source=${PWD},target=/workspace,readonly" --workdir /workspace ponderadacomp-backend:local python client/terminal.py --url http://backend:6767
```

Espere o backend aparecer como `healthy` no primeiro comando. O segundo executa [client/terminal.py](client/terminal.py), consulta `GET /health` e faz `POST /predict` para o primeiro dia aceito. O resultado esperado é HTTP `200` e um JSON com `ds` (data) e `yhat` (previsão em USD por BTC). Dentro da rede Docker, o endereço do serviço é `http://backend:6767`.

Para escolher uma data, acrescente-a ao final do comando do cliente, por exemplo `2026-10-05`. Com os dados incluídos, a API aceita **2026-10-05 a 2026-10-11**, os sete dias após o fim do treino. Datas fora desse intervalo retornam HTTP `422`.

Se já tiver Python instalado, também pode consultar a API pelo terminal do computador:

```sh
python client/terminal.py
```

### 5. Encerrar

Use `Ctrl+C` no terminal da API e depois execute, na raiz do repo:

```sh
docker compose down
```

Esse comando remove os containers e a rede do projeto. Os CSVs e modelos permanecem na pasta do repo; a imagem Docker pode ser reutilizada.

## Dados incluídos no repo

Os CSVs contêm **preços públicos de mercado de BTC-USD obtidos do [Yahoo Finance](https://finance.yahoo.com/quote/BTC-USD/history/)** e estão versionados para reproduzir o experimento sem uma nova coleta. Não contêm dados pessoais.

| Arquivo | Período | Linhas | Tamanho |
| --- | --- | ---: | ---: |
| [data/processed/btc_usd_daily.csv](data/processed/btc_usd_daily.csv) | 2023-10-05 a 2026-10-04 | 1.096 | 26,3 KiB |
| [data/processed/btc_usd_daily_12y.csv](data/processed/btc_usd_daily_12y.csv) | 2014-09-17 a 2026-10-04 | 4.401 | 113,6 KiB |

As colunas são `ds` (data diária) e `y` (fechamento em USD por BTC). A [procedência](data/README.md) registra a fonte, os períodos e os hashes SHA-256. Preserve os arquivos e os metadados juntos: o treinamento confere os hashes antes de ajustar os modelos.

Para repetir a coleta, opcionalmente, use a mesma imagem Docker. Estes comandos sobrescrevem os respectivos CSVs e metadados; dependem da internet e o Yahoo pode revisar preços históricos:

```sh
docker run --rm --user 0:0 --mount "type=bind,source=${PWD},target=/workspace" --workdir /workspace ponderadacomp-backend:local python data/download_btc.py
docker run --rm --user 0:0 --mount "type=bind,source=${PWD},target=/workspace" --workdir /workspace ponderadacomp-backend:local python data/download_btc.py --start 2014-09-17 --end 2026-10-05 --output data/processed/btc_usd_daily_12y.csv --metadata data/coleta-btc-usd-12y.json
```

## ARIMA opcional

O backend usa Prophet. Para reproduzir a comparação exploratória ARIMA, execute depois do treinamento Prophet, em um ambiente Python 3.13 local, versão usada nesse experimento:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --no-cache-dir --only-binary=:all: -r requirements-arima.txt
.venv\Scripts\python.exe training/train_arima.py
```

Esse script usa também os relatórios e CSVs de previsões gerados pelo Prophet. Gera `models/arima.json` separado; ele não substitui o modelo carregado pela API. Veja [training/README.md](training/README.md) para versões e testes.

## Resultados e documentação

Os relatórios versionados registram a execução original no Windows com Python 3.13. O roteiro Docker usa Linux com Python 3.12 e gera seus próprios relatórios em `reports/`; os valores e hashes dos modelos podem diferir entre ambientes, mesmo com os mesmos CSVs.

Na verificação deste roteiro em 05/10/2026, o clone limpo construiu a imagem, treinou Prophet, passou nos cinco testes de treinamento e retornou HTTP `200` pelo cliente. Os hashes dos CSVs foram preservados. O MAE do teste de 90 dias foi USD 16.867,51 (três anos) e USD 29.041,29 (12 anos); repetir o último fechamento teve menor erro, USD 8.707,09. Essa comparação não comprova precisão no horizonte de sete dias da API.

- [Resultados Prophet](reports/comparacao.md) e [ARIMA](reports/arima.md).
- [Contrato da API e evidência Docker](backend/README.md), [cliente](client/README.md) e [integração registrada](reports/integracao.json).
- [Arquitetura](docs/arquitetura.md), [requisitos](docs/requisitos.md) e [devlog](DEVLOG.md).
- [Enunciado da atividade](https://github.com/Murilo-ZC/Atividade-Ponderada-M7-2026-EC).
