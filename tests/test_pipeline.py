import duckdb
import pytest

from pipeline_consumidor import runner
from pipeline_consumidor.cli import main

HEADER = ("Região;UF;Cidade;Sexo;Faixa Etária;Ano Abertura;Mês Abertura;Data Abertura;Data Resposta;Data Finalização;"
          "Tempo Resposta;Nome Fantasia;Segmento de Mercado;Área;Assunto;Grupo Problema;Problema;"
          "Como Comprou Contratou;Procurou Empresa;Respondida;Situação;Avaliação Reclamação;Nota do Consumidor")


def linha(uf="SP", data="04/03/2026", tempo="3", empresa="Banco A", resp="S", situacao="Finalizada avaliada - Resolvida",
          nota="5"):
    return (f"Sudeste;{uf};Cidade;M;faixa;2026;3;{data};;;{tempo};{empresa};Bancos;Área;Assunto;Grupo;Problema;"
            f"Loja;S;{resp};{situacao};Avaliação;{nota}")


def csv_com(tmp_path, linhas):
    caminho = tmp_path / "entrada.csv"
    caminho.write_text("\n".join([HEADER, *linhas]) + "\n", encoding="utf-8")
    return caminho


@pytest.fixture(scope="module")
def amostra(tmp_path_factory):
    db = tmp_path_factory.mktemp("amostra") / "c.duckdb"
    assert runner.construir(runner.CSV_PADRAO, db)
    return db


def test_amostra_passa_em_todos_os_testes_de_qualidade(amostra):
    c = runner.contagens(amostra)
    assert c["bronze_reclamacoes"] == 600
    assert c["silver_reclamacoes"] == 600
    assert c["gold_ranking_empresas"] > 0


def test_ouro_soma_igual_a_prata(amostra):
    con = duckdb.connect(str(amostra))
    total = con.execute("select sum(reclamacoes) from gold_ranking_empresas").fetchone()[0]
    mensal = con.execute("select sum(reclamacoes) from gold_serie_mensal").fetchone()[0]
    con.close()
    assert total == mensal == 600


def test_prata_tipa_data_e_marca_nao_resolvida(tmp_path):
    csv = csv_com(tmp_path, [linha(), linha(situacao="Finalizada avaliada - Não Resolvida", nota="1")])
    db = tmp_path / "m.duckdb"
    assert runner.construir(csv, db)
    con = duckdb.connect(str(db))
    linhas = con.execute("select data_abertura::varchar, nao_resolvida from silver_reclamacoes order by nota desc").fetchall()
    con.close()
    assert linhas == [("2026-03-04", False), ("2026-03-04", True)]


def test_teste_de_qualidade_barra_nota_fora_da_escala(tmp_path):
    csv = csv_com(tmp_path, [linha(nota="9")])
    assert not runner.construir(csv, tmp_path / "ruim.duckdb")


def test_teste_de_qualidade_barra_uf_invalida(tmp_path):
    csv = csv_com(tmp_path, [linha(uf="XX")])
    assert not runner.construir(csv, tmp_path / "uf.duckdb")


def test_volume_barra_descarte_excessivo(tmp_path):
    # 3 de 4 linhas sem data válida: a prata perde 75% e o teste de volume reprova
    csv = csv_com(tmp_path, [linha(), linha(data="x"), linha(data="y"), linha(data="z")])
    assert not runner.construir(csv, tmp_path / "volume.duckdb")


def test_cli_rodar_e_ranking(tmp_path, capsys):
    db = tmp_path / "cli.duckdb"
    assert main(["rodar", "--db", str(db)]) == 0
    assert "silver_reclamacoes: 600 linhas" in capsys.readouterr().out
    assert main(["ranking", "--db", str(db), "--limite", "2"]) == 0
    assert capsys.readouterr().out.count("reclamações") == 2


def test_cli_arquivo_inexistente(tmp_path, capsys):
    assert main(["rodar", "--csv", str(tmp_path / "nada.csv"), "--db", str(tmp_path / "x.duckdb")]) == 1
    assert "não encontrado" in capsys.readouterr().err
    assert main(["ranking", "--db", str(tmp_path / "nao_existe.duckdb")]) == 1
