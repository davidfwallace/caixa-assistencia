import sqlite3
from datetime import date

import pytest

from caixa.estoque import EstoqueInsuficiente, ItemEstoque
from caixa.modelos import ENTRADA, SAIDA
from caixa.repositorio import RepositorioLancamentos
from caixa.repositorio_estoque import RepositorioEstoque

HOJE = date(2026, 10, 19)


@pytest.fixture
def caminho(tmp_path):
    return tmp_path / "teste.db"


def novo_item(**mudancas):
    dados = dict(peca="Bateria", variante="", modelo="iPhone 11", quantidade=10,
                 custo_centavos=8990, preco_centavos=25000)
    dados.update(mudancas)
    return ItemEstoque(**dados)


def test_item_cadastrado_recebe_id_e_aparece_na_lista(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(novo_item())
    assert item.id is not None
    assert [i.nome for i in estoque.listar()] == ["Bateria — iPhone 11"]


def test_item_duplicado_e_recusado(caminho):
    estoque = RepositorioEstoque(caminho)
    estoque.adicionar_item(novo_item())
    with pytest.raises(ValueError):
        estoque.adicionar_item(novo_item())


def test_buscar_item_inexistente_da_erro(caminho):
    with pytest.raises(ValueError):
        RepositorioEstoque(caminho).buscar(999)


def test_conserto_baixa_estoque_e_lanca_entrada(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(novo_item(quantidade=10))

    estoque.registrar_uso(item.id, HOJE, 25000)

    assert estoque.buscar(item.id).quantidade == 9
    [lancamento] = RepositorioLancamentos(caminho).listar()
    assert lancamento.categoria == "Conserto"
    assert lancamento.tipo == ENTRADA
    assert lancamento.descricao == "Bateria — iPhone 11"
    assert lancamento.item_id == item.id


def test_venda_de_acessorio_usa_a_categoria_certa(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(
        novo_item(peca="Película", variante="Vidro 3D", preco_centavos=3000)
    )
    lancamento = estoque.registrar_uso(item.id, HOJE, 3000)
    assert lancamento.categoria == "Venda de acessório"


def test_uso_sem_estoque_da_erro_e_nao_lanca_nada(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(novo_item(quantidade=0))

    with pytest.raises(EstoqueInsuficiente):
        estoque.registrar_uso(item.id, HOJE, 25000)

    assert estoque.buscar(item.id).quantidade == 0
    assert RepositorioLancamentos(caminho).listar() == []


def test_uso_com_valor_invalido_nao_altera_estoque(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(novo_item(quantidade=10))

    with pytest.raises(ValueError):
        estoque.registrar_uso(item.id, HOJE, 0)

    assert estoque.buscar(item.id).quantidade == 10
    assert RepositorioLancamentos(caminho).listar() == []


def test_compra_soma_estoque_atualiza_custo_e_lanca_saida(caminho):
    estoque = RepositorioEstoque(caminho)
    item = estoque.adicionar_item(novo_item(quantidade=10, custo_centavos=8990))

    lancamento = estoque.registrar_compra(item.id, 5, 9500, HOJE)

    atualizado = estoque.buscar(item.id)
    assert atualizado.quantidade == 15
    assert atualizado.custo_centavos == 9500
    assert lancamento.tipo == SAIDA
    assert lancamento.categoria == "Peças"
    assert lancamento.valor_centavos == 47500  # 5 x R$ 95,00


def test_migracao_atualiza_banco_antigo_sem_perder_dados(caminho):
    # Simula o banco da versão anterior, sem a coluna item_id
    conexao = sqlite3.connect(caminho)
    conexao.execute(
        "CREATE TABLE lancamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, "
        "descricao TEXT, categoria TEXT, valor_centavos INTEGER, tipo TEXT)"
    )
    conexao.execute(
        "INSERT INTO lancamentos (data, descricao, categoria, valor_centavos, tipo) "
        "VALUES ('2026-10-03', 'Troca antiga', 'Conserto', 25000, 'entrada')"
    )
    conexao.commit()
    conexao.close()

    [lancamento] = RepositorioLancamentos(caminho).listar()
    assert lancamento.descricao == "Troca antiga"
    assert lancamento.item_id is None