# Backend de inferência

Reservado para o serviço Python e seu Dockerfile. Ainda não implementado.

Proposta inicial de interface: `GET /health` para verificar disponibilidade e `POST /predict` para solicitar uma predição. Os caminhos são uma proposta, não endpoints já existentes.

O serviço deve validar entradas e usar o mesmo contrato de preparação dos dados do treinamento.
