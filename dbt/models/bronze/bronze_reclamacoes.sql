-- Bronze: o CSV do jeito que chegou (tudo texto), só com nomes de coluna sem acento.
select
    "UF" as uf,
    "Cidade" as cidade,
    "Data Abertura" as data_abertura,
    "Tempo Resposta" as tempo_resposta,
    "Nome Fantasia" as nome_fantasia,
    "Segmento de Mercado" as segmento_de_mercado,
    "Grupo Problema" as grupo_problema,
    "Problema" as problema,
    "Respondida" as respondida,
    "Situação" as situacao,
    "Nota do Consumidor" as nota_do_consumidor
from read_csv('{{ var("csv") }}', delim=';', header=true, all_varchar=true)
