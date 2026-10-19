from caixa.modelos import Lancamento, ENTRADA, SAIDA


def filtrar_por_mes(lancamentos: list[Lancamento], ano: int, mes: int) -> list[Lancamento]:
    return [l for l in lancamentos if l.data.year == ano and l.data.month == mes]


def total_por_tipo(lancamentos: list[Lancamento], tipo: str) -> int:
    return sum(l.valor_centavos for l in lancamentos if l.tipo == tipo)


def saldo(lancamentos: list[Lancamento]) -> int:
    return total_por_tipo(lancamentos, ENTRADA) - total_por_tipo(lancamentos, SAIDA)


def total_por_categoria(lancamentos: list[Lancamento]) -> dict[str, int]:
    totais = {}
    for l in lancamentos:
        totais[l.categoria] = totais.get(l.categoria, 0) + l.valor_centavos
    return totais