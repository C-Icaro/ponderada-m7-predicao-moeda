# Artefatos

Reservado para `models/modelo.json`, a ser gerado pelo notebook. Nenhum artefato existe neste checkpoint.

A proposta usa a serialização nativa do Prophet: `model_to_json` para exportar e `model_from_json` para carregar. O backend Python lerá esse arquivo por um volume Docker somente leitura, em `/app/models/modelo.json`.

Essa escolha segue a [documentação oficial de Saving models](https://facebook.github.io/prophet/docs/additional_topics.html#saving-models), que desaconselha pickle para os modelos Prophet em Python.

Registrar campos e unidades da entrada, horizonte, dependências e referência aos dados. Arquivos de modelos ficam ignorados por padrão; documentar no notebook como gerar novamente o artefato.
