from datetime import date

import pytest

from caixa.modelos import ENTRADA, Lancamento


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
])
def test_lancamento_invalido_e_recusado(campo, valor):
    with pytest.raises(ValueError):
        criar(**{campo: valor})