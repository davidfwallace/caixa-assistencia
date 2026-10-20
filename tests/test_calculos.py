from datetime import date

from caixa.calculos import filtrar_por_mes, saldo, total_por_categoria
from caixa.modelos import ENTRADA, SAIDA, Lancamento, Perda
from caixa.calculos import (
    filtrar_por_mes, lucro_bruto, lucro_por_item, margem_percentual,
    saldo, total_por_categoria,
)


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

def conserto(valor, custo, nome="Bateria — iPhone 11", item_id=1):
    return Lancamento(date(2026, 10, 3), nome, "Conserto", valor, ENTRADA,
                      item_id=item_id, custo_centavos=custo)


def test_lucro_bruto_desconta_so_o_custo_das_pecas_usadas():
    lancamentos = [
        conserto(25000, 8990),
        lanc(5, 3000),                         # avulso: custo zero
        lanc(6, 50000, SAIDA),                 # compra de estoque: não entra no lucro
    ]
    assert lucro_bruto(lancamentos) == 25000 + 3000 - 8990


def test_margem_sem_receita_e_none():
    assert margem_percentual([]) is None


def test_margem_percentual():
    # Lucro de 16010 sobre receita de 25000 = 64,04%
    assert margem_percentual([conserto(25000, 8990)]) == 64.0


def test_lucro_por_item_agrupa_e_ordena_do_maior_pro_menor():
    lancamentos = [
        conserto(40000, 20000, nome="Tela Frontal — iPhone XR", item_id=2),
        conserto(25000, 8990),
        conserto(25000, 8990),
        lanc(7, 3000),  # avulso, sem item: fica de fora
    ]
    ranking = lucro_por_item(lancamentos)

    assert [r.nome for r in ranking] == ["Bateria — iPhone 11", "Tela Frontal — iPhone XR"]
    assert ranking[0].quantidade == 2
    assert ranking[0].receita_centavos == 50000
    assert ranking[0].lucro_centavos == 32020


def test_perdas_reduzem_o_lucro_bruto():
    perda = Perda(date(2026, 10, 10), 1, "Bateria — iPhone 11", 1, 8990, "Troca em garantia")
    assert lucro_bruto([conserto(25000, 8990)], [perda]) == 25000 - 8990 - 8990