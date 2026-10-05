# Artefatos

Reservado para `models/modelo.joblib`, a ser gerado pelo notebook. Nenhum artefato existe neste checkpoint.

A proposta é salvar um modelo simples com as transformações necessárias à inferência, se usadas. O backend Python lerá esse arquivo por um volume Docker somente leitura, em `/app/models/modelo.joblib`.

Registrar campos e unidades da entrada, horizonte, dependências e referência aos dados. Arquivos de modelos ficam ignorados por padrão; documentar no notebook como gerar novamente o artefato.
