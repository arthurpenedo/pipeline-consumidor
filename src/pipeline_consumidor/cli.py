"""CLI.

    pipeline-consumidor rodar [--csv dados/amostra_sintetica.csv] [--db consumidor.duckdb]
    pipeline-consumidor ranking [--db consumidor.duckdb] [--limite 5]
"""

import argparse
import sys
from pathlib import Path

import duckdb

from . import runner


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="pipeline-consumidor")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("rodar", help="constrói bronze, prata e ouro e roda os testes de qualidade")
    p.add_argument("--csv", type=Path, default=runner.CSV_PADRAO)
    p.add_argument("--db", type=Path, default=Path("consumidor.duckdb"))
    p = sub.add_parser("ranking", help="mostra o topo do ranking de empresas (camada ouro)")
    p.add_argument("--db", type=Path, default=Path("consumidor.duckdb"))
    p.add_argument("--limite", type=int, default=5)
    args = parser.parse_args(argv)

    if args.cmd == "rodar":
        if not args.csv.is_file():
            print(f"Arquivo não encontrado: {args.csv}", file=sys.stderr)
            return 1
        if args.db.is_dir():
            print(f"--db precisa ser um arquivo .duckdb, mas {args.db} é uma pasta.", file=sys.stderr)
            return 2
        if not runner.construir(args.csv, args.db):
            print("O pipeline falhou: veja os testes acima.", file=sys.stderr)
            return 1
        for tabela, n in runner.contagens(args.db).items():
            print(f"{tabela}: {n} linhas")
        return 0

    if args.limite < 1:  # erro de uso vem antes de olhar a base, como nos outros projetos
        print("--limite deve ser pelo menos 1", file=sys.stderr)
        return 2
    if not args.db.is_file():
        print(f"Base não encontrada: {args.db} (rode `pipeline-consumidor rodar` antes)", file=sys.stderr)
        return 1
    try:
        linhas = runner.ranking(args.db, args.limite)
    except duckdb.CatalogException:
        print(f"{args.db} não tem a camada ouro (rode `pipeline-consumidor rodar` antes)", file=sys.stderr)
        return 1
    except duckdb.IOException:  # arquivo existe mas não é uma base DuckDB
        print(f"{args.db} não é uma base DuckDB válida", file=sys.stderr)
        return 1
    for empresa, n, pct, nota in linhas:
        print(f"{empresa}: {n} reclamações, {pct}% respondidas, nota média {nota}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
