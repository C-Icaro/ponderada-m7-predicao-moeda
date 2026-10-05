# Backend de inferência

Reservado para o serviço Python e seu Dockerfile. A proposta usa um único container de inferência. Ainda não implementado.

O serviço carregará `models/modelo.joblib` do host por um volume somente leitura, disponível no container como `/app/models/modelo.joblib`.

Proposta inicial de interface: `GET /health` para verificar disponibilidade e `POST /predict` para solicitar uma predição. Os caminhos são uma proposta, não endpoints já existentes.

O serviço deve validar entradas e usar o mesmo contrato de preparação dos dados do treinamento.
