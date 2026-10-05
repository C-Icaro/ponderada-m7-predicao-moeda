# Escopo e critérios de aceite

Fonte: [enunciado da atividade](https://github.com/Murilo-ZC/Atividade-Ponderada-M7-2026-EC), referência `471310e2b792d5ab9759c4774300f4c4c3dd7777`.

## Entrega a desenvolver

| ID | Resultado esperado | Evidência de aceite |
| --- | --- | --- |
| R01 | UML da solução mínima e troca de dados | CSV, notebook, artefato, único container de inferência e terminal; transferência por volume somente leitura |
| R02 | Um notebook treina Prophet com CSV pequeno | Colunas `ds` e `y`, divisão cronológica treino/teste e exportação de `models/modelo.json` |
| R03 | Backend Python em um único container Docker | Carrega o artefato pelo volume somente leitura; interfaces propostas `GET /health` e `POST /predict` |
| R04 | Solicitação pelo terminal | Comando `curl` ou `Invoke-RestMethod` executado e resposta contendo predição |
| R05 | Devlog no GitHub | Decisões, dificuldades, comandos e resultados verificáveis |

A separação de treino e teste será cronológica, sem embaralhamento. A primeira versão usará Prophet com data e preço, conforme recomendação do professor relatada pelo autor. A precisão é secundária à demonstração da integração.

O escopo mínimo é um notebook, um modelo simples, um artefato, um container de inferência e o terminal como cliente.

## Decisões abertas

- Horizonte de previsão e campos da entrada.
- Configuração inicial do Prophet e métrica de avaliação.
- Capacidade local para executar Docker, considerando o espaço livre.

## Aceite deste checkpoint

Repositório privado criado, registro original e imagem preservados, arquitetura simples documentada e coleta diária de BTC-USD do Yahoo Finance validada: três anos, 1.096 registros de 05/10/2023 a 04/10/2026, CSV local de 26.968 bytes. Script de obtenção e procedência registrados. Nenhum notebook de treinamento, modelo exportado, backend ou container foi implementado ou executado.
