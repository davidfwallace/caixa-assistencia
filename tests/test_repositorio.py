from datetime import date

from caixa.modelos import ENTRADA, SAIDA, Lancamento
from caixa.repositorio import RepositorioLancamentos


def criar_lancamento(dia=3, descricao="Troca de bateria iPhone 11"):
    return Lancamento(date(2026, 10, dia), descricao, "Conserto", 25000, ENTRADA)


def test_banco_novo_comeca_vazio(tmp_path):
    repo = RepositorioLancamentos(tmp_path / "teste.db")
    assert repo.listar() == []


def test_lancamento_salvo_volta_igual(tmp_path):
    repo = RepositorioLancamentos(tmp_path / "teste.db")
    original = criar_lancamento()
    repo.adicionar(original)
    assert repo.listar() == [original]


def test_dados_persistem_entre_conexoes(tmp_path):
    caminho = tmp_path / "teste.db"
    RepositorioLancamentos(caminho).adicionar(criar_lancamento())
    # Um repositório novo, apontando pro mesmo arquivo, enxerga o dado salvo
    assert len(RepositorioLancamentos(caminho).listar()) == 1


def test_listar_ordena_por_data(tmp_path):
    repo = RepositorioLancamentos(tmp_path / "teste.db")
    repo.adicionar(criar_lancamento(dia=20))
    repo.adicionar(Lancamento(date(2026, 10, 5), "Bateria", "Peças", 8990, SAIDA))
    assert [l.data.day for l in repo.listar()] == [5, 20]


def test_texto_malicioso_e_salvo_como_texto(tmp_path):
    repo = RepositorioLancamentos(tmp_path / "teste.db")
    malicioso = "x'); DROP TABLE lancamentos; --"
    repo.adicionar(criar_lancamento(descricao=malicioso))
    # A tabela continua existindo e o texto voltou intacto
    assert repo.listar()[0].descricao == malicioso