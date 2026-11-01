-- Ouro: ranking de empresas por volume, com taxa de resposta, nota média e tempo médio.
select
    empresa,
    segmento,
    count(*) as reclamacoes,
    round(100.0 * avg(respondida::int), 1) as pct_respondidas,
    round(avg(nota), 2) as nota_media,
    round(avg(tempo_resposta_dias), 1) as tempo_medio_dias,
    round(100.0 * avg(nao_resolvida::int), 1) as pct_nao_resolvidas
from {{ ref('silver_reclamacoes') }}
group by empresa, segmento
order by reclamacoes desc, empresa
