"""Roda o projeto dbt por Python e lê o resultado das camadas no DuckDB."""

import json
import os
from pathlib import Path

import duckdb
from dbt.cli.main import dbtRunner

RAIZ = Path(__file__).resolve().parents[2]
DBT_DIR = RAIZ / "dbt"
CSV_PADRAO = RAIZ / "dados" / "amostra_sintetica.csv"


def construir(csv: Path = CSV_PADRAO, db: Path = Path("consumidor.duckdb")) -> bool:
    """`dbt build`: cria bronze, prata e ouro e roda os testes de qualidade. True se tudo passou."""
    os.environ["PIPELINE_DB"] = str(Path(db).resolve())
    args = ["build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR),
            "--vars", json.dumps({"csv": str(Path(csv).resolve())}),
            "--target-path", str(Path(db).resolve().parent / ".dbt-target")]
    return dbtRunner().invoke(args).success


def contagens(db: Path) -> dict[str, int]:
    """Linhas de cada tabela das três camadas."""
    con = duckdb.connect(str(db))
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("bronze_reclamacoes", "silver_reclamacoes", "gold_ranking_empresas", "gold_serie_mensal")}
    finally:
        con.close()


def ranking(db: Path, limite: int = 5) -> list[tuple]:
    con = duckdb.connect(str(db))
    try:
        return con.execute("select empresa, reclamacoes, pct_respondidas, nota_media from gold_ranking_empresas limit ?",
                           [limite]).fetchall()
    finally:
        con.close()
