from dataclasses import dataclass

from caixa.catalogo import MODELOS, PECAS

ESTOQUE_MINIMO_PADRAO = 5


class EstoqueInsuficiente(ValueError):
    """Erro de quando se tenta usar mais peças do que existem no estoque."""


@dataclass
class ItemEstoque:
    peca: str
    variante: str
    modelo: str
    quantidade: int
    custo_centavos: int
    preco_centavos: int
    minimo: int = ESTOQUE_MINIMO_PADRAO
    id: int | None = None  # preenchido pelo banco na parte 2

    def __post_init__(self):
        if self.peca not in PECAS:
            raise ValueError(f"Peça desconhecida: {self.peca}")
        variantes = PECAS[self.peca]
        if variantes and self.variante not in variantes:
            raise ValueError(f"Variante inválida para {self.peca}: {self.variante}")
        if not variantes and self.variante:
            raise ValueError(f"{self.peca} não tem variantes.")
        if self.modelo not in MODELOS:
            raise ValueError(f"Modelo desconhecido: {self.modelo}")
        if self.quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        if self.custo_centavos < 0:
            raise ValueError("O custo não pode ser negativo.")
        if self.preco_centavos <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        if self.minimo < 0:
            raise ValueError("O estoque mínimo não pode ser negativo.")

    @property
    def nome(self) -> str:
        peca = f"{self.peca} {self.variante}" if self.variante else self.peca
        return f"{peca} — {self.modelo}"

    @property
    def precisa_repor(self) -> bool:
        return self.quantidade <= self.minimo

    def baixar(self, quantidade: int = 1) -> None:
        if quantidade <= 0:
            raise ValueError("A quantidade a baixar deve ser maior que zero.")
        if quantidade > self.quantidade:
            raise EstoqueInsuficiente(
                f"Sem estoque suficiente de {self.nome} (disponível: {self.quantidade})."
            )
        self.quantidade -= quantidade

    def repor(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("A quantidade a repor deve ser maior que zero.")
        self.quantidade += quantidade


def itens_para_repor(itens: list[ItemEstoque]) -> list[ItemEstoque]:
    return [item for item in itens if item.precisa_repor]


def gerar_pedido(itens: list[ItemEstoque]) -> str:
    """Monta a mensagem de pedido ao fornecedor com os itens em falta."""
    em_falta = itens_para_repor(itens)
    if not em_falta:
        return ""
    linhas = ["Olá! Gostaria de fazer um pedido:"]
    for item in em_falta:
        linhas.append(f"- {item.nome} (tenho {item.quantidade} em estoque)")
    return "\n".join(linhas)