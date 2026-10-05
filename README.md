# Ponderada M7: predição de moeda com Python e Docker

Repositório de Carlos Paiva para desenvolver a atividade ponderada de Computação, M7, EC 2026.

**Estado atual:** notebooks Prophet e ARIMA executados, comparações registradas e artefatos JSON exportados. Backend Python e cliente terminal implementados, com Dockerfile e Compose na porta `6767` e rede `PonderadaComp`.

## Referência

[Enunciado do professor Murilo](https://github.com/Murilo-ZC/Atividade-Ponderada-M7-2026-EC), consultado em 05/10/2026, commit de referência `471310e2b792d5ab9759c4774300f4c4c3dd7777`.

## Objetivo

Construir uma demonstração que conecte dados históricos, treinamento, exportação do modelo, inferência em um backend Python conteinerizado e uma solicitação feita por um cliente.

## Organização

| Caminho | Finalidade |
| --- | --- |
| [DEVLOG.md](DEVLOG.md) | Registro do processo, decisões e evidências |
| [docs/requisitos.md](docs/requisitos.md) | Escopo e critérios de aceite |
| [docs/arquitetura.md](docs/arquitetura.md) | Arquitetura de componentes e interfaces propostas |
| [docs/arquitetura.mmd](docs/arquitetura.mmd) e [docs/pipeline.mmd](docs/pipeline.mmd) | Nova versão editável em Mermaid |
| [docs/sequencia.mmd](docs/sequencia.mmd) | Ordem das interações entre notebook, artefato, backend e terminal |
| [docs/imagens/esboco-pipeline-original.png](docs/imagens/esboco-pipeline-original.png) | Esboço enviado pelo autor |
| [data/README.md](data/README.md) | Obtenção, contrato, tamanho e procedência de BTC-USD |
| [training/README.md](training/README.md) | Ambiente de treinamento e exportação |
| [training/comparacao.ipynb](training/comparacao.ipynb) | Notebook executado com a comparação de três e 12 anos |
| [training/train_compare.py](training/train_compare.py) | Implementação compartilhada pelo notebook e terminal |
| [training/protocolo.md](training/protocolo.md) | Cortes e critérios definidos antes dos resultados |
| [requirements-training.txt](requirements-training.txt) | Versões das dependências usadas |
| [reports/comparacao.md](reports/comparacao.md) | Resultados medidos, gráfico e limites |
| [training/arima.ipynb](training/arima.ipynb) e [reports/arima.md](reports/arima.md) | Experimento exploratório ARIMA e confronto com Prophet |
| [models/README.md](models/README.md) | Artefatos do modelo |
| [backend/README.md](backend/README.md) | Serviço de inferência em Python |
| [client/README.md](client/README.md) | Cliente para demonstrar a predição |
| [reports/integracao.json](reports/integracao.json) | Requisições reais, imagem Docker, rede, porta e hash do backend |

## Primeira versão e comparação

Os CSVs são separados: três anos (05/10/2023 a 04/10/2026, 1.096 registros, 26,3 KiB) e aproximadamente 12 anos (17/09/2014 a 04/10/2026, 4.401 registros, 113,6 KiB). Os preços nas datas comuns são idênticos. [Obtenção e procedência](data/README.md).

O notebook usa a mesma configuração Prophet nas duas janelas. Escolhe pelo MAE da validação e avalia os mesmos 90 dias finais, de 07/07/2026 a 04/10/2026, sem usar esse teste para escolher a janela.

| Versão | MAE no teste, USD por BTC |
| --- | ---: |
| Prophet com três anos | 16.347,51 |
| Prophet com aproximadamente 12 anos | 28.836,89 |
| Referência: repetir último fechamento conhecido | 8.707,09 |

Três anos tiveram menor erro na validação e no teste. A janela longa teve MAE de teste 76,4% maior, mas a referência simples superou os dois Prophet. Esse resultado se limita à configuração e aos períodos avaliados. [Relatório completo](reports/comparacao.md).

O ajuste final de três anos, com dados até 04/10/2026, gerou `models/modelo.json` usado pelo backend. Esse ajuste final ainda não possui avaliação independente. Para reproduzir o treinamento pelo terminal após a preparação descrita em [training](training/README.md):

```powershell
.\.venv\Scripts\python.exe training/train_compare.py
```

## ARIMA exploratório

Depois de ver os resultados Prophet, foram comparadas quatro ordens ARIMA previamente fixadas, usando as mesmas datas. A validação escolheu `(0,1,0)` nas duas janelas e três anos pelo desempate. O MAE de teste foi USD 8.707,09, igual à referência de repetir o último fechamento conhecido. Esse resultado não demonstrou ganho sobre a referência simples. A etapa é exploratória, pois o teste já era conhecido. [Protocolo e reprodução](training/README.md#experimento-exploratório-arima).

## Executar o backend e consultar pelo terminal

Após obter os dados e executar o treinamento Prophet, o arquivo `models/modelo.json` precisa existir. No terminal da raiz do projeto:

```text
docker compose up --build -d --wait
python client/terminal.py
docker compose down
```

O cliente consulta `http://127.0.0.1:6767/health` e usa a primeira data permitida para pedir uma previsão. Também pode receber uma data: `python client/terminal.py 2026-10-05`. A API aceita os sete dias seguintes ao fim do treino, atualmente 05/10/2026 a 11/10/2026. O volume do modelo é somente leitura; a rede se chama `PonderadaComp`. [Comandos PowerShell e Docker via WSL, respostas e verificações](backend/README.md).

Neste computador, Docker está no WSL Ubuntu-24.04. Mantenha a execução no primeiro terminal e consulte pelo segundo terminal Windows:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose --project-name ponderadacomp up --build --pull never
```

O container foi verificado como saudável e respondeu ao cliente Windows com HTTP 200. A [evidência da integração](reports/integracao.json) confirma o volume somente leitura, rede, porta e correspondência do hash do código local com o código na imagem. A primeira previsão funcional foi `78248.948192546` USD para 05/10/2026, sem avaliação independente da precisão desse reajuste final.

Referências técnicas: [Quick Start do Prophet](https://facebook.github.io/prophet/docs/quick_start.html) e [serialização oficial em JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).

## Limitações

A comparação mede previsões de 90 dias feitas de uma vez, a partir de um corte fixo. Esse período é diferente do horizonte operacional de sete dias da API. Os CSVs e modelos gerados ficam fora do Git; código, notebooks executados, procedência e resultados permitem reproduzi-los. Os limites e a evidência de integração estão no [devlog](DEVLOG.md). As predições futuras são experimentais.
