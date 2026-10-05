# Dados

Nenhum conjunto de dados foi baixado neste checkpoint.

Antes da coleta, registrar fonte/URL, moeda/par, moeda de cotação, período, frequência, fuso horário, colunas, unidade e licença/condições de uso.

Planejar inicialmente um CSV pequeno. O tamanho depende do número de observações e colunas. Medir o arquivo real antes de ampliar o recorte.

Contrato proposto para Prophet: converter a coluna de data para `ds` e a de preço de fechamento para `y`, numérica. A primeira versão usará apenas essas duas colunas, conforme o [Quick Start oficial](https://facebook.github.io/prophet/docs/quick_start.html).

Os arquivos em `data/raw/` e `data/processed/` ficam fora do Git por padrão. Se um pequeno conjunto puder ser redistribuído, sua inclusão deve ser uma decisão explícita; caso contrário, documentar a obtenção.
