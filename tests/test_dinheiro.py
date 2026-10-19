import pytest

from caixa.dinheiro import formatar_reais, reais_para_centavos


@pytest.mark.parametrize("texto, esperado", [
    ("49,90", 4990),
    ("49,9", 4990),
    ("30", 3000),
    ("1.299,90", 129990),
    ("R$ 250,00", 25000),
    ("  10,00  ", 1000),
])
def test_converte_formatos_validos(texto, esperado):
    assert reais_para_centavos(texto) == esperado


@pytest.mark.parametrize("texto", ["-5,00", "49.90", "10,999", "abc", "", "1,2,3"])
def test_recusa_formatos_invalidos(texto):
    with pytest.raises(ValueError):
        reais_para_centavos(texto)


@pytest.mark.parametrize("centavos, esperado", [
    (4990, "R$ 49,90"),
    (5, "R$ 0,05"),
    (0, "R$ 0,00"),
    (129990, "R$ 1.299,90"),
    (100000000, "R$ 1.000.000,00"),
    (-450, "-R$ 4,50"),
])
def test_formata_reais(centavos, esperado):
    assert formatar_reais(centavos) == esperado


def test_ida_e_volta_preserva_o_valor():
    assert formatar_reais(reais_para_centavos("1.299,90")) == "R$ 1.299,90"


def test_soma_em_centavos_nao_tem_erro_de_arredondamento():
    # Com float, a soma direta tem erro: 0.1 + 0.2 dá 0.30000000000000004
    assert 0.1 + 0.2 != 0.3
    # Com centavos inteiros, a conta fecha exatamente
    assert reais_para_centavos("0,10") + reais_para_centavos("0,20") == reais_para_centavos("0,30")