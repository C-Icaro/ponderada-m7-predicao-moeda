# Ponderada M7: predição de moeda com Python e Docker

Repositório de Carlos Paiva para desenvolver a atividade ponderada de Computação, M7, EC 2026.

**Estado atual:** notebook executado, Prophet treinado com três anos e com o histórico longo, comparação registrada e modelos exportados em JSON. Backend e containers ainda estão pendentes.

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
| [models/README.md](models/README.md) | Artefatos do modelo |
| [backend/README.md](backend/README.md) | Serviço de inferência em Python |
| [client/README.md](client/README.md) | Cliente para demonstrar a predição |

## Primeira versão e comparação

Os CSVs são separados: três anos (05/10/2023 a 04/10/2026, 1.096 registros, 26,3 KiB) e aproximadamente 12 anos (17/09/2014 a 04/10/2026, 4.401 registros, 113,6 KiB). Os preços nas datas comuns são idênticos. [Obtenção e procedência](data/README.md).

O notebook usa a mesma configuração Prophet nas duas janelas. Escolhe pelo MAE da validação e avalia os mesmos 90 dias finais, de 07/07/2026 a 04/10/2026, sem usar esse teste para escolher a janela.

| Versão | MAE no teste, USD por BTC |
| --- | ---: |
| Prophet com três anos | 16.347,51 |
| Prophet com aproximadamente 12 anos | 28.836,89 |
| Referência: repetir último fechamento conhecido | 8.707,09 |

Três anos tiveram menor erro na validação e no teste. A janela longa teve MAE de teste 76,4% maior, mas a referência simples superou os dois Prophet. Esse resultado se limita à configuração e aos períodos avaliados. [Relatório completo](reports/comparacao.md).

O ajuste final de três anos, com dados até 04/10/2026, gerou `models/modelo.json` para a próxima integração. Esse ajuste final ainda não possui avaliação independente. Para reproduzir o treinamento pelo terminal após a preparação descrita em [training](training/README.md):

```powershell
.\.venv\Scripts\python.exe training/train_compare.py
```

## Próxima etapa

Implementar o backend Python em um único container Docker, carregar o modelo JSON e demonstrar a solicitação pelo terminal com `curl` ou `Invoke-RestMethod`. Definir o horizonte aceito pela API e verificar o espaço necessário para Docker.

Referências técnicas: [Quick Start do Prophet](https://facebook.github.io/prophet/docs/quick_start.html) e [serialização oficial em JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).

## Limitações

A comparação mede previsões de 90 dias feitas de uma vez, a partir de um corte fixo. Serviço HTTP e container ainda não foram executados. Os CSVs e modelos gerados ficam fora do Git; código, notebook executado, procedência e resultados permitem reproduzi-los. As predições futuras serão experimentais, sem finalidade de recomendação de investimento.
