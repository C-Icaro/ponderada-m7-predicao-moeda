# Ponderada M7: predição de moeda com Python e Docker

Repositório de Carlos Paiva para desenvolver a atividade ponderada de Computação, M7, EC 2026.

**Estado atual:** preparação do projeto. Ainda não há coleta de dados, modelo treinado, backend ou containers executados.

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
| [docs/imagens/esboco-pipeline-original.png](docs/imagens/esboco-pipeline-original.png) | Esboço enviado pelo autor |
| [data/README.md](data/README.md) | Contrato e procedência dos dados, a definir |
| [training/README.md](training/README.md) | Ambiente de treinamento e exportação |
| [models/README.md](models/README.md) | Artefatos do modelo |
| [backend/README.md](backend/README.md) | Serviço de inferência em Python |
| [client/README.md](client/README.md) | Cliente para demonstrar a predição |

## Próxima decisão

Definir moeda/par, fonte, frequência, período e horizonte previsto. A proposta usa Prophet, recomendado pelo professor segundo o relato do autor: CSV com `ds` (data) e `y` (preço), treinamento em notebook, exportação para `models/modelo.json`, backend Python em um container Docker e uso pelo terminal (`curl` ou `Invoke-RestMethod`). O desenvolvimento será registrado no devlog, com comandos e resultados efetivamente observados.

Referências técnicas: [Quick Start do Prophet](https://facebook.github.io/prophet/docs/quick_start.html) e [serialização oficial em JSON](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).

## Limitações

Não há comandos de execução da solução neste checkpoint porque ela ainda não foi implementada. As predições futuras serão experimentais, sem finalidade de recomendação de investimento.
