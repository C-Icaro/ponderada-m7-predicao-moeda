# Backend de inferência

Reservado para o serviço Python e seu Dockerfile. A proposta usa um único container de inferência. Ainda não implementado.

O serviço carregará `models/modelo.json` do host por um volume somente leitura, disponível no container como `/app/models/modelo.json`.

Proposta inicial de interface: `GET /health` para verificar disponibilidade e `POST /predict` para solicitar uma predição. Os caminhos são uma proposta, não endpoints já existentes.

O serviço deve carregar `models/modelo.json` com `prophet.serialize.model_from_json`. A operação de predição receberá a data `ds`, chamará `modelo.predict` com essa coluna e devolverá `ds` e `yhat` em JSON. Fonte: [Quick Start do Prophet](https://facebook.github.io/prophet/docs/quick_start.html).

Validar a data e o horizonte aceito antes da predição. O formato final da requisição e a configuração continuam sendo propostas.
