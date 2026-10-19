import pytest

from caixa.estoque import EstoqueInsuficiente, ItemEstoque, gerar_pedido, itens_para_repor


def criar_item(**mudancas):
    dados = dict(
        peca="Bateria",
        variante="",
        modelo="iPhone 11",
        quantidade=10,
        custo_centavos=8990,
        preco_centavos=25000,
    )
    dados.update(mudancas)
    return ItemEstoque(**dados)


def test_nome_sem_variante():
    assert criar_item().nome == "Bateria — iPhone 11"


def test_nome_com_variante():
    item = criar_item(peca="Tela", variante="Frontal", modelo="iPhone XR")
    assert item.nome == "Tela Frontal — iPhone XR"


@pytest.mark.parametrize("mudancas", [
    {"peca": "Antena"},                      # peça que não existe
    {"peca": "Tela", "variante": "Lateral"}, # variante que não existe
    {"peca": "Tela", "variante": ""},        # Tela exige variante
    {"variante": "Frontal"},                 # Bateria não tem variante
    {"modelo": "Galaxy S24"},                # modelo fora do catálogo
    {"quantidade": -1},
    {"custo_centavos": -1},
    {"preco_centavos": 0},
    {"minimo": -1},
])
def test_item_invalido_e_recusado(mudancas):
    with pytest.raises(ValueError):
        criar_item(**mudancas)


@pytest.mark.parametrize("quantidade, esperado", [
    (6, False),  # logo acima do mínimo
    (5, True),   # exatamente no mínimo
    (0, True),   # zerado
])
def test_precisa_repor_no_limite(quantidade, esperado):
    assert criar_item(quantidade=quantidade).precisa_repor == esperado


def test_minimo_personalizado():
    assert criar_item(quantidade=3, minimo=2).precisa_repor is False


def test_baixar_reduz_quantidade():
    item = criar_item(quantidade=10)
    item.baixar()
    assert item.quantidade == 9


def test_baixar_alem_do_disponivel_da_erro_e_nao_altera():
    item = criar_item(quantidade=1)
    with pytest.raises(EstoqueInsuficiente):
        item.baixar(2)
    assert item.quantidade == 1


def test_baixar_ultima_unidade_zera():
    item = criar_item(quantidade=1)
    item.baixar()
    assert item.quantidade == 0


def test_repor_aumenta_quantidade():
    item = criar_item(quantidade=3)
    item.repor(10)
    assert item.quantidade == 13


@pytest.mark.parametrize("quantidade", [0, -5])
def test_repor_quantidade_invalida_da_erro(quantidade):
    with pytest.raises(ValueError):
        criar_item().repor(quantidade)


def test_itens_para_repor_filtra_os_baixos():
    itens = [criar_item(quantidade=10), criar_item(modelo="iPhone 12", quantidade=4)]
    assert [i.modelo for i in itens_para_repor(itens)] == ["iPhone 12"]


def test_pedido_lista_so_itens_em_falta():
    itens = [criar_item(quantidade=10), criar_item(modelo="iPhone 12", quantidade=4)]
    pedido = gerar_pedido(itens)
    assert "Bateria — iPhone 12 (tenho 4 em estoque)" in pedido
    assert "iPhone 11" not in pedido


def test_pedido_vazio_quando_nada_falta():
    assert gerar_pedido([criar_item(quantidade=10)]) == ""