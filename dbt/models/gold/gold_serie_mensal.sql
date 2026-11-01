-- Ouro: reclamações por mês e segmento.
select
    date_trunc('month', data_abertura)::date as mes,
    segmento,
    count(*) as reclamacoes
from {{ ref('silver_reclamacoes') }}
group by 1, 2
order by 1, 2
