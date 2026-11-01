-- Falha se a prata perder mais de 5% das linhas da bronze (muito descarte = problema na origem).
select b.n as bronze, s.n as prata
from (select count(*) as n from {{ ref('bronze_reclamacoes') }}) b,
     (select count(*) as n from {{ ref('silver_reclamacoes') }}) s
where s.n < 0.95 * b.n
