# Escopo e critérios de aceite

Fonte: [enunciado da atividade](https://github.com/Murilo-ZC/Atividade-Ponderada-M7-2026-EC), referência `471310e2b792d5ab9759c4774300f4c4c3dd7777`.

## Entrega a desenvolver

| ID | Resultado esperado | Evidência de aceite |
| --- | --- | --- |
| R01 | UML da solução mínima e troca de dados | CSV, notebook, artefato, único container de inferência e terminal; transferência por volume somente leitura |
| R02 | Um notebook treina Prophet com CSV pequeno | Colunas `ds` e `y`, divisão cronológica treino/validação/teste, comparação das janelas e exportação de `models/modelo.json` |
| R03 | Backend Python em um único container Docker | Carrega o artefato pelo volume somente leitura; `GET /health` e `POST /predict`; porta `6767` e rede `PonderadaComp` solicitadas pelo autor |
| R04 | Solicitação pelo terminal | Comando `curl` ou `Invoke-RestMethod` executado e resposta contendo predição |
| R05 | Devlog no GitHub | Decisões, dificuldades, comandos e resultados verificáveis |
| R06 | Comparação ARIMA solicitada pelo autor | Ordens fixadas antes dos ajustes, seleção por validação, confronto exploratório com Prophet e referência simples |

A separação de treino, validação e teste é cronológica, sem embaralhamento. A primeira versão usa Prophet com data e preço, conforme recomendação do professor relatada pelo autor. A precisão é secundária à demonstração da integração. O pedido posterior do autor acrescentou a comparação entre três e aproximadamente 12 anos de histórico, com seleção pelo MAE de validação antes do teste final.

O escopo mínimo é um notebook, um modelo simples, um artefato, um container de inferência e o terminal como cliente.

## Contrato de inferência

Entrada: somente `{"ds":"YYYY-MM-DD"}`. Saída com data, `yhat` em USD por BTC e identificação do artefato. Horizonte de sete dias após a data final do treino. Datas inválidas ou fora desse intervalo retornam `422`; JSON inválido retorna `400`. Artefato ausente ou inválido impede a inicialização. O cliente terminal faz requisições HTTP reais.

## Aceite deste checkpoint

R02 foi executado: [notebook](../training/comparacao.ipynb), [protocolo](../training/protocolo.md), [métricas e gráfico](../reports/comparacao.md), exportação dos dois modelos avaliados e do ajuste final escolhido. Os CSVs foram validados e os modelos recarregados reproduziram as previsões. Cinco testes verificam métricas, cortes temporais, seleção e casos de borda do relatório.

R01 e R05 têm documentação e registros publicados. R03 e R04 têm implementação e validação descritas em [backend](../backend/README.md) e [devlog](../DEVLOG.md), com Dockerfile, Compose e cliente terminal. R06 foi executado no [notebook ARIMA](../training/arima.ipynb); o [relatório](../reports/arima.md) preserva o empate com a referência e os limites do teste já observado.
