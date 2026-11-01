-- Prata: tipos corretos, texto limpo e linhas sem data ou empresa descartadas (o teste de volume vigia o descarte).
with tipada as (
    select
        upper(trim(uf)) as uf,
        trim(cidade) as cidade,
        coalesce(try_strptime(data_abertura, '%d/%m/%Y'), try_strptime(data_abertura, '%Y-%m-%d'))::date as data_abertura,
        try_cast(nullif(trim(tempo_resposta), '') as integer) as tempo_resposta_dias,
        trim(nome_fantasia) as empresa,
        trim(segmento_de_mercado) as segmento,
        trim(grupo_problema) as grupo_problema,
        trim(problema) as problema,
        upper(trim(respondida)) in ('S', 'SIM') as respondida,
        trim(situacao) as situacao,
        try_cast(nullif(trim(nota_do_consumidor), '') as integer) as nota
    from {{ ref('bronze_reclamacoes') }}
)
select
    *,
    coalesce(situacao ilike '%não resolvida%', false) as nao_resolvida
from tipada
where data_abertura is not null and empresa is not null and empresa <> ''
