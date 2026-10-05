# Backend de inferência

O [serviço implementado](app.py) usa HTTP da biblioteca padrão do Python para a demonstração local da ponderada. Ele carrega `models/modelo.json` uma vez, com `prophet.serialize.model_from_json`, verifica uma previsão e somente então abre a porta **6767**. Ausência ou corrupção do artefato interrompe a inicialização com código de saída 1. Alterar o JSON exige reiniciar o serviço.

O modelo continua sendo Prophet. A [comparação de treinamento](../reports/comparacao.md) e a implementação de inferência são etapas distintas. O backend usa o reajuste final de três anos, treinado até 04/10/2026, identificado pelo SHA-256 `8fcd04e80bd236a8a879be335a19acc80830b47d0e030aae3044fc0421a716c1`.

## Contrato HTTP

| Operação | Entrada | Resultado |
| --- | --- | --- |
| `GET /health` | Sem corpo | HTTP 200, modelo carregado, hash, fim do treino e intervalo aceito |
| `POST /predict` | `Content-Type: application/json`, somente `{"ds":"YYYY-MM-DD"}` | HTTP 200 com `ds`, `yhat`, unidade, par, modelo e hash |

O horizonte da API é fixo em sete dias após a última data do treino. Para o artefato atual, aceita **05/10/2026 a 11/10/2026**, inclusive. A data precisa existir no calendário e usar exatamente `YYYY-MM-DD`; datas do treino ou posteriores ao horizonte são rejeitadas. `/health` informa esse intervalo para o cliente.

Resposta real obtida no container para 05/10/2026:

```json
{
  "ds": "2026-10-05",
  "yhat": 78248.948192546,
  "symbol": "BTC-USD",
  "currency": "USD",
  "model": "Prophet",
  "trained_until": "2026-10-04",
  "model_sha256": "8fcd04e80bd236a8a879be335a19acc80830b47d0e030aae3044fc0421a716c1"
}
```

`yhat` é a previsão de fechamento em USD por BTC. Esse reajuste final não tem avaliação independente posterior a 04/10/2026. O horizonte de sete dias da API também difere da avaliação anterior, que previu blocos de 90 dias; as métricas daquela comparação não comprovam desempenho deste novo horizonte.

| Situação | HTTP |
| --- | ---: |
| JSON vazio, malformado ou incompleto | 400 |
| Endpoint inexistente | 404 |
| GET em `/predict` ou POST em `/health` | 405 |
| Corpo maior que 4.096 bytes | 413 |
| Content-Type diferente de JSON | 415 |
| Campo, tipo, formato, data ou horizonte inválido | 422 |
| Falha ao gerar uma previsão finita | 500 |

Erros retornam `{"error":{"code":"...","message":"..."}}` em JSON.

## Execução com Docker

Pré-requisito: gerar o artefato seguindo [training](../training/README.md). O [Dockerfile](../Dockerfile) usa uma base Python 3.12 slim identificada por digest e instala somente pacotes binários, sem cache. O [Compose](../compose.yaml) publica `127.0.0.1:6767`, cria a rede com nome **PonderadaComp** e monta `models/` como `/app/models` somente para leitura. O modelo não entra na imagem. O container executa como usuário `app`.

Neste computador, Docker Engine e Compose estão disponíveis na distribuição WSL `Ubuntu-24.04`. Na raiz do repositório, em PowerShell:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose --project-name ponderadacomp build --pull=false
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose --project-name ponderadacomp up --no-build --pull never
```

Mantenha esse primeiro terminal aberto e execute o [cliente](../client/README.md) em um segundo terminal Windows. A execução foi verificada em primeiro plano. Uma tentativa anterior em modo destacado terminou com código 255 após ficar sem chamada WSL ativa, sem exceção da aplicação no log; não assumimos persistência ao fechar o terminal ou encerrar a distribuição. Não foi alterada a configuração global do WSL.

Onde Docker já estiver disponível diretamente no terminal, o comando equivalente é `docker compose --project-name ponderadacomp up --build`. Para encerrar, use Ctrl+C no terminal de execução. Para remover somente o container e a rede deste projeto:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose --project-name ponderadacomp down
```

A imagem base já existia localmente e foi reaproveitada. `docker image ls` mediu **571 MB** para `ponderadacomp-backend:local`; esse valor inclui camadas compartilhadas e não equivale ao crescimento observado em C:. Ao concluir a verificação, havia aproximadamente **2,59 GiB livres** em C:, acima do piso de 1 GiB definido para esta execução. Nenhuma imagem ou dado preexistente foi removido.

## Execução local e verificação

Também é possível executar usando o ambiente já preparado para Prophet:

```powershell
.venv\Scripts\python.exe backend/app.py
```

O endereço padrão fora do container é `http://127.0.0.1:6767`. `--host`, `--port` e `--model` permitem configurar a execução manual; o Compose mantém a porta requerida em 6767. As dependências estão em [requirements-backend.txt](../requirements-backend.txt).

```powershell
.venv\Scripts\python.exe -m unittest discover -s backend -p "test_*.py"
```

Nove testes passaram com o artefato real: saúde, previsão nos limites, validação de entrada, formato de corpo, endpoints, modelo ausente/corrompido e cliente terminal por HTTP, incluindo erro HTML sem traceback. No Docker, também foram comprovados saúde, previsões, oito situações inválidas, volume de leitura, porta, rede e falhas de inicialização com artefato ausente/corrompido. A [evidência registrada](../reports/integracao.json) contém respostas, hashes do código, identificação da imagem e comandos.

Referências: [API de previsão do Prophet](https://facebook.github.io/prophet/docs/quick_start.html), [serialização JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models), [HTTP da biblioteca padrão](https://docs.python.org/3.13/library/http.server.html) e [nome da rede no Compose](https://docs.docker.com/reference/compose-file/networks/#name).
