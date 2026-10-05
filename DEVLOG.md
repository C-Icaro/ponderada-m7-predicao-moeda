# Devlog

## 05/10/2026

### Registro original do autor

Texto preservado como recebido:

> 14:17 - Começo da ponderada: Leitura do material
>
> 14:23 - Dúvidas levantadas: Qual moeda escolher? Minha suposição é que bitcoin precisaria de um volume de dados muito grande, que meu ssd com 10gb livres não iriam suportar. Mas também suponho que para prever dollar preciariamos correlacionar muitas variáveis da politica internacional
>
> 14:25 - Esboço do diagrama UML
>
> 14:32 - Revisão do esboço com IA: GPT 6.1 Sol Ultra em Fast Mode

A identificação da ferramenta acima é o registro informado pelo autor.

![Esboço original: recebimento dos dados, EDA, limpeza, feature engineering, treinamento, seleção e avaliação](docs/imagens/esboco-pipeline-original.png)

### Preparação do repositório com IA

- Enunciado consultado no repositório indicado pelo autor.
- Estrutura inicial criada para dados, treinamento, modelos, backend e cliente.
- Moeda e implementação permanecem pendentes.
- O dado "10gb livres" acima foi preservado como percepção inicial. A inspeção do ambiente encontrou aproximadamente 2,84 GiB livres em C:, sinal que pode mudar com o uso do computador.
- Nenhum treinamento, container ou resultado de predição foi executado nesta preparação.

### Próxima etapa

Revisar a arquitetura de componentes e definir um recorte pequeno de dados antes de implementar o treinamento.

### Revisão proposta da arquitetura com IA

- O esboço original foi preservado como pipeline de construção do modelo. A [arquitetura de componentes proposta](docs/arquitetura.md), com [fonte UML](docs/arquitetura.puml), complementa esse registro.
- A proposta conecta CSV, ambiente de treinamento, artefato com modelo e transformações, volume `models/` somente leitura, backend Python em Docker e cliente HTTP. `GET /health` e `POST /predict` são interfaces propostas.
- O pipeline detalhado inclui divisão cronológica, validação para seleção e teste final reservado. Transformações que aprendem parâmetros serão ajustadas somente no treino.
- Moeda, fonte, horizonte, formato do artefato, modelo e implementação continuam abertos. Esta revisão não representa treinamento executado nem predição demonstrada.

### Nova versão em Mermaid, solicitada pelo autor

- O formato visual foi alterado para Mermaid após o pedido de edição no Excalidraw.
- Foram criados dois diagramas: arquitetura da solução e pipeline detalhado de ML. O esboço original permanece preservado.
- A revisão acrescenta exportação do artefato, montagem em volume somente leitura, backend, cliente e troca HTTP/JSON.
- No pipeline, a revisão explicita divisão cronológica, validação, teste final reservado e exportação das transformações.

### Simplificação solicitada pelo autor

- A interface de uso será o terminal, com `curl` ou `Invoke-RestMethod`.
- A proposta atual usa um CSV pequeno, um notebook, um modelo exportado e um container de backend Python.
- A divisão inicial será treino/teste cronológica. A comparação entre vários modelos e a validação adicional da proposta anterior ficam como extensões opcionais.
- A versão Mermaid foi ajustada a esse escopo. A revisão acima permanece como registro da evolução, e a [arquitetura atual](docs/arquitetura.md) descreve a proposta vigente.

### Validação da documentação

- Os dois diagramas Mermaid foram renderizados no Mermaid Live no navegador. Essa verificação confirma a sintaxe e a apresentação dos diagramas, não a execução da solução.
- Exportações SVG e capturas do editor foram preservadas em `docs/imagens/`.
- [Captura da arquitetura](docs/imagens/arquitetura-mermaid-editor.jpg) e [captura do pipeline](docs/imagens/pipeline-mermaid-editor.jpg).

### Recomendação do professor: Prophet

- O autor informou que o professor recomendou o [Quick Start do Prophet](https://facebook.github.io/prophet/docs/quick_start.html). A proposta foi ajustada para usar essa biblioteca com `ds` (data) e `y` (preço).
- O artefato proposto mudou de Joblib para `models/modelo.json`, usando `model_to_json` e `model_from_json`, conforme a [documentação de serialização](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models).
- O backend receberá a data `ds` e devolverá a previsão `yhat`. O terminal continua sendo a interface de uso.
- A avaliação será feita apenas nas datas do teste reservado. O histórico incluído por padrão em `make_future_dataframe` não será tratado como resultado de teste.
- Este checkpoint atualiza a documentação. Prophet ainda não foi instalado nem executado. A proposta anterior e suas capturas permanecem recuperáveis no [commit 2911e61](https://github.com/C-Icaro/ponderada-m7-predicao-moeda/commit/2911e61b310f7d18bfef6a49634dde743b5c7a42).

### Busca e coleta de BTC-USD no Yahoo Finance

- O autor solicitou buscar um histórico adequado à limitação de espaço. Foi obtido um recorte diário de 05/10/2024 a 04/10/2026, com 730 registros. Uma observação diária evita o volume de negociações individuais que motivou a dúvida inicial.
- A página histórica retornou HTTP 429 na ferramenta de pesquisa; a consulta do endpoint de histórico do Yahoo pelo Python local respondeu normalmente. A coleta foi executada com `python data/download_btc.py`, usando apenas a biblioteca padrão, sem instalar pacotes.
- O CSV `data/processed/btc_usd_daily.csv` tem somente `ds` (data da fonte UTC) e `y` (fechamento em USD por BTC). Tamanho medido: 17.853 bytes, aproximadamente 17,4 KiB. A inspeção encontrou cerca de 2,81 GiB livres em C:.
- O Yahoo retornou uma observação adicional de 05/10/2026; ela foi removida pelo filtro de fim exclusivo. Foram conferidos intervalo completo, duplicatas, lacunas, valores finitos e positivos, tamanho e SHA-256. A leitura pelo pandas já disponível no ambiente também foi validada.
- [Procedência da coleta](data/coleta-btc-usd.json) e [instruções de obtenção](data/README.md) foram registradas. Os preços permanecem em arquivo local ignorado pelo Git; script e metadados são os artefatos versionados para reprodução.
- A divisão proposta é treino com 640 registros até 06/07/2026 e teste com os últimos 90 dias, de 07/07/2026 a 04/10/2026. O horizonte de uso futuro e a configuração do Prophet continuam pendentes. Nenhum modelo foi treinado; o tamanho do ambiente Python e Docker ainda não foi medido.

### Ampliação para três anos, solicitada pelo autor

- Após a primeira coleta, o autor pediu pelo menos três anos. O início foi alterado para 05/10/2023 e a coleta foi executada novamente. O recorte vigente vai até 04/10/2026, com 1.096 observações diárias, incluindo 29/02/2024.
- O CSV atual mede 26.968 bytes, aproximadamente 26,3 KiB. Permanece com apenas `ds` e `y`, sem incluir o dia em andamento. Script, procedência e documentação foram atualizados para esse intervalo.
- A série atual foi validada novamente quanto a datas consecutivas, ausência de duplicatas/lacunas, fechamentos finitos e positivos, leitura pelo pandas, tamanho e hash. O teste proposto mantém os últimos 90 dias; o treino passa a ter 1.006 registros.
- A coleta de dois anos acima é o registro da etapa anterior. Nenhum modelo foi treinado nesta ampliação.
