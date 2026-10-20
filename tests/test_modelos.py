from datetime import date

import pytest

from caixa.modelos import ENTRADA, SAIDA, Lancamento, Perda


def criar(**mudancas):
    dados = dict(
        data=date(2026, 10, 1),
        descricao="Troca de bateria",
        categoria="Conserto",
        valor_centavos=25000,
        tipo=ENTRADA,
    )
    dados.update(mudancas)
    return Lancamento(**dados)


def test_lancamento_valido_e_criado():
    lancamento = criar()
    assert lancamento.valor_centavos == 25000


@pytest.mark.parametrize("campo, valor", [
    ("valor_centavos", 0),
    ("valor_centavos", -100),
    ("tipo", "transferencia"),
    ("categoria", "Peças"),   # Peças é categoria de saída, não de entrada
    ("descricao", "   "),
    ("custo_centavos", -1),
])
def test_lancamento_invalido_e_recusado(campo, valor):
    with pytest.raises(ValueError):
        criar(**{campo: valor})


def test_saida_com_custo_e_recusada():
    with pytest.raises(ValueError):
        criar(tipo=SAIDA, categoria="Peças", custo_centavos=100)

def criar_perda(**mudancas):
    dados = dict(
        data=date(2026, 10, 10),
        item_id=1,
        descricao="Bateria — iPhone 11",
        quantidade=2,
        custo_unitario_centavos=8990,
        motivo="Troca em garantia",
    )
    dados.update(mudancas)
    return Perda(**dados)


def test_custo_total_da_perda():
    assert criar_perda().custo_total_centavos == 17980


@pytest.mark.parametrize("campo, valor", [
    ("quantidade", 0),
    ("custo_unitario_centavos", -1),
    ("motivo", "Sumiu"),
])
def test_perda_invalida_e_recusada(campo, valor):
    with pytest.raises(ValueError):
        criar_perda(**{campo: valor})