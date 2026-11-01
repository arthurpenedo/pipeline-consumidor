# pipeline-consumidor

Pipeline de dados em **camadas (bronze → prata → ouro)** com **dbt** e **DuckDB** sobre reclamações no formato do [consumidor.gov.br](https://www.consumidor.gov.br/), com **testes de qualidade de dados** que reprovam o pipeline quando a entrada vem estragada.

## O que faz
| Camada | Modelo | O que acontece |
|---|---|---|
| Bronze | `bronze_reclamacoes` | lê o CSV (`;`) tudo como texto, com nomes de coluna sem acento |
| Prata | `silver_reclamacoes` | tipa data, nota e tempo; limpa texto; descarta linha sem data ou empresa; marca `nao_resolvida` |
| Ouro | `gold_ranking_empresas`, `gold_serie_mensal` | ranking por empresa (volume, % respondidas, nota média, tempo médio) e série mensal por segmento |

Testes de qualidade (`dbt build` roda modelos e testes juntos): `not_null`, `unique`, `accepted_values` (UF válida, nota de 1 a 5), um teste genérico próprio (`nao_negativo`) e um de **volume** (a prata não pode perder mais de 5% das linhas da bronze).

## Resultado medido (amostra sintética de 600 reclamações, 1 execução local)
- `dbt build`: 4 modelos + 11 testes, **15 de 15 passaram** em cerca de 1,4 s.
- Linhas: bronze 600 → prata 600 → ouro 7 empresas e 24 linhas na série mensal.
- Os 8 testes em Python (`pytest`) incluem entradas estragadas (nota 9, UF "XX", 3 de 4 datas inválidas) e conferem que o pipeline **falha** nelas.

Os dados da amostra são **fictícios** (copiados do [reclamacoes-radar](https://github.com/arthurpenedo/reclamacoes-radar)); com um CSV oficial do consumidor.gov.br (`--csv`), as mesmas camadas valem.

## Como rodar
```bash
pip install -e ".[dev]"
pipeline-consumidor rodar                       # constrói as camadas e roda os testes
pipeline-consumidor ranking --limite 5          # topo do ranking (camada ouro)
pipeline-consumidor rodar --csv meu_arquivo.csv --db meu.duckdb
python -m pytest -q
```
Ou direto no dbt: `cd dbt && dbt build --profiles-dir .`

## Decisão de projeto: DuckDB no lugar de PySpark
A ideia inicial era PySpark local. PySpark exige Java instalado e é pesado para 600 linhas (ou para milhões, no tamanho que um PC aguenta); o DuckDB faz o mesmo SQL em colunas, sem servidor, e o dbt-duckdb mantém o padrão de mercado (camadas, `ref`, testes, documentação). A estrutura de camadas serve igual se um dia a origem for grande a ponto de pedir Spark.

## Limites
- A amostra é sintética; não há aqui nenhuma medição com o arquivo oficial completo.
- Carga é completa a cada execução (tabelas recriadas), sem incremental.
- Orquestração (Airflow) fica fora desta primeira versão.
