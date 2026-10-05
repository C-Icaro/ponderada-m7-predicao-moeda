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
