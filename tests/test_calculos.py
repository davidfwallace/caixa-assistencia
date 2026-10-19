from datetime import date

from caixa.calculos import filtrar_por_mes, saldo, total_por_categoria
from caixa.modelos import ENTRADA, SAIDA, Lancamento


def lanc(dia, valor, tipo=ENTRADA, categoria=None, ano=2026, mes=10):
    if categoria is None:
        categoria = "Conserto" if tipo == ENTRADA else "Peças"
    return Lancamento(date(ano, mes, dia), "teste", categoria, valor, tipo)


def test_saldo_de_lista_vazia_e_zero():
    assert saldo([]) == 0


def test_saldo_e_entradas_menos_saidas():
    assert saldo([lanc(1, 25000), lanc(2, 8990, SAIDA)]) == 16010


def test_saldo_pode_ficar_negativo():
    assert saldo([lanc(1, 1000), lanc(2, 5000, SAIDA)]) == -4000


def test_filtrar_por_mes_respeita_os_limites():
    lancamentos = [
        lanc(30, 100, mes=9),            # último dia do mês anterior
        lanc(1, 200, mes=10),            # primeiro dia do mês
        lanc(31, 300, mes=10),           # último dia do mês
        lanc(1, 400, mes=11),            # primeiro dia do mês seguinte
        lanc(15, 500, ano=2025, mes=10), # mesmo mês, outro ano
    ]
    resultado = filtrar_por_mes(lancamentos, 2026, 10)
    assert [l.valor_centavos for l in resultado] == [200, 300]


def test_total_por_categoria_agrupa_valores():
    lancamentos = [
        lanc(1, 25000),
        lanc(2, 32000),
        lanc(3, 3000, categoria="Venda de acessório"),
        lanc(4, 8990, SAIDA),
    ]
    assert total_por_categoria(lancamentos) == {
        "Conserto": 57000,
        "Venda de acessório": 3000,
        "Peças": 8990,
    }