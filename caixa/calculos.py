from caixa.modelos import Lancamento, ENTRADA, SAIDA
from dataclasses import dataclass


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

def custo_das_pecas(lancamentos: list[Lancamento]) -> int:
    return sum(l.custo_centavos for l in lancamentos if l.tipo == ENTRADA)


@dataclass
class ResumoItem:
    nome: str
    quantidade: int
    receita_centavos: int
    lucro_centavos: int


def lucro_por_item(lancamentos: list[Lancamento]) -> list[ResumoItem]:
    """Agrupa consertos e vendas por item do estoque, do mais lucrativo pro menos."""
    resumos = {}
    for l in lancamentos:
        if l.tipo != ENTRADA or l.item_id is None:
            continue
        resumo = resumos.setdefault(l.descricao, ResumoItem(l.descricao, 0, 0, 0))
        resumo.quantidade += 1
        resumo.receita_centavos += l.valor_centavos
        resumo.lucro_centavos += l.valor_centavos - l.custo_centavos
    return sorted(resumos.values(), key=lambda r: r.lucro_centavos, reverse=True)

def custo_das_perdas(perdas) -> int:
    return sum(p.custo_total_centavos for p in perdas)


def lucro_bruto(lancamentos: list[Lancamento], perdas=()) -> int:
    """Receitas menos o custo das peças usadas e das peças perdidas."""
    return (
        total_por_tipo(lancamentos, ENTRADA)
        - custo_das_pecas(lancamentos)
        - custo_das_perdas(perdas)
    )


def margem_percentual(lancamentos: list[Lancamento], perdas=()) -> float | None:
    receita = total_por_tipo(lancamentos, ENTRADA)
    if receita == 0:
        return None
    return round(lucro_bruto(lancamentos, perdas) / receita * 100, 1)