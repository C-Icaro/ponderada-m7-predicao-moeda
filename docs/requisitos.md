# Escopo e critérios de aceite

Fonte: [enunciado da atividade](https://github.com/Murilo-ZC/Atividade-Ponderada-M7-2026-EC), referência `471310e2b792d5ab9759c4774300f4c4c3dd7777`.

## Entrega a desenvolver

| ID | Resultado esperado | Evidência de aceite |
| --- | --- | --- |
| R01 | UML da solução mínima e troca de dados | CSV, notebook, artefato, único container de inferência e terminal; transferência por volume somente leitura |
| R02 | Um notebook treina Prophet com CSV pequeno | Colunas `ds` e `y`, divisão cronológica treino/validação/teste, comparação das janelas e exportação de `models/modelo.json` |
| R03 | Backend Python em um único container Docker | Carrega o artefato pelo volume somente leitura; interfaces propostas `GET /health` e `POST /predict` |
| R04 | Solicitação pelo terminal | Comando `curl` ou `Invoke-RestMethod` executado e resposta contendo predição |
| R05 | Devlog no GitHub | Decisões, dificuldades, comandos e resultados verificáveis |

A separação de treino, validação e teste é cronológica, sem embaralhamento. A primeira versão usa Prophet com data e preço, conforme recomendação do professor relatada pelo autor. A precisão é secundária à demonstração da integração. O pedido posterior do autor acrescentou a comparação entre três e aproximadamente 12 anos de histórico, com seleção pelo MAE de validação antes do teste final.

O escopo mínimo é um notebook, um modelo simples, um artefato, um container de inferência e o terminal como cliente.

## Decisões abertas

- Horizonte de previsão e campos da entrada.
- Capacidade local para executar Docker, considerando o espaço livre.

## Aceite deste checkpoint

R02 foi executado: [notebook](../training/comparacao.ipynb), [protocolo](../training/protocolo.md), [métricas e gráfico](../reports/comparacao.md), exportação dos dois modelos avaliados e do ajuste final escolhido. Os CSVs foram validados e os modelos recarregados reproduziram as previsões. Cinco testes verificam métricas, cortes temporais, seleção e casos de borda do relatório.

R01 e R05 têm documentação e registros publicados. R03 e R04 permanecem pendentes: nenhum backend HTTP, Dockerfile ou container foi implementado ou executado neste checkpoint.
