from dataclasses import dataclass
from datetime import date

ENTRADA = "entrada"
SAIDA = "saida"

CATEGORIAS = {
    ENTRADA: ["Conserto", "Venda de seminovo", "Venda de acessório"],
    SAIDA: ["Peças", "Compra de aparelho", "Estoque de acessórios", "Despesas fixas"],
}


@dataclass
class Lancamento:
    data: date
    descricao: str
    categoria: str
    valor_centavos: int
    tipo: str
    item_id: int | None = None
    custo_centavos: int = 0

    def __post_init__(self):
        if self.tipo not in CATEGORIAS:
            raise ValueError(f"Tipo inválido: {self.tipo}")
        if self.categoria not in CATEGORIAS[self.tipo]:
            raise ValueError(f"Categoria '{self.categoria}' não existe para {self.tipo}.")
        if self.valor_centavos <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        if not self.descricao.strip():
            raise ValueError("A descrição não pode ficar vazia.")
        if self.custo_centavos < 0:
            raise ValueError("O custo não pode ser negativo.")