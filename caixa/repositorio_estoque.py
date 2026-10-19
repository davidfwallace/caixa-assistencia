import sqlite3
from datetime import date
from pathlib import Path

from caixa.banco import abrir, inicializar
from caixa.catalogo import SERVICOS
from caixa.estoque import ItemEstoque
from caixa.modelos import ENTRADA, SAIDA, Lancamento
from caixa.repositorio import inserir_lancamento

COLUNAS = "id, peca, variante, modelo, quantidade, custo_centavos, preco_centavos, minimo"


def _item_da_linha(linha) -> ItemEstoque:
    item_id, peca, variante, modelo, quantidade, custo, preco, minimo = linha
    return ItemEstoque(peca, variante, modelo, quantidade, custo, preco, minimo, item_id)


def _buscar(conexao, item_id: int) -> ItemEstoque:
    linha = conexao.execute(
        f"SELECT {COLUNAS} FROM estoque WHERE id = ?", (item_id,)
    ).fetchone()
    if linha is None:
        raise ValueError("Item de estoque não encontrado.")
    return _item_da_linha(linha)


class RepositorioEstoque:
    def __init__(self, caminho_banco: str | Path):
        self.caminho_banco = caminho_banco
        inicializar(caminho_banco)

    def adicionar_item(self, item: ItemEstoque) -> ItemEstoque:
        """Cadastra um item com o estoque que você já tem em mãos."""
        try:
            with abrir(self.caminho_banco) as conexao:
                cursor = conexao.execute(
                    "INSERT INTO estoque "
                    "(peca, variante, modelo, quantidade, custo_centavos, preco_centavos, minimo) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (item.peca, item.variante, item.modelo, item.quantidade,
                     item.custo_centavos, item.preco_centavos, item.minimo),
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"{item.nome} já está cadastrado no estoque.")
        item.id = cursor.lastrowid
        return item

    def listar(self) -> list[ItemEstoque]:
        with abrir(self.caminho_banco) as conexao:
            linhas = conexao.execute(
                f"SELECT {COLUNAS} FROM estoque ORDER BY peca, variante, modelo"
            ).fetchall()
        return [_item_da_linha(linha) for linha in linhas]

    def buscar(self, item_id: int) -> ItemEstoque:
        with abrir(self.caminho_banco) as conexao:
            return _buscar(conexao, item_id)

    def registrar_uso(self, item_id: int, data: date, valor_centavos: int) -> Lancamento:
        """Conserto ou venda de acessório: baixa 1 do estoque e lança a entrada no caixa."""
        with abrir(self.caminho_banco) as conexao:
            item = _buscar(conexao, item_id)
            item.baixar()
            categoria = "Conserto" if item.peca in SERVICOS else "Venda de acessório"
            lancamento = Lancamento(data, item.nome, categoria, valor_centavos, ENTRADA, item.id)
            conexao.execute(
                "UPDATE estoque SET quantidade = ? WHERE id = ?", (item.quantidade, item.id)
            )
            inserir_lancamento(conexao, lancamento)
        return lancamento

    def registrar_compra(self, item_id: int, quantidade: int,
                         custo_unitario_centavos: int, data: date) -> Lancamento:
        """Compra do fornecedor: soma no estoque, atualiza o custo e lança a saída no caixa."""
        with abrir(self.caminho_banco) as conexao:
            item = _buscar(conexao, item_id)
            item.repor(quantidade)
            item.custo_centavos = custo_unitario_centavos
            categoria = "Peças" if item.peca in SERVICOS else "Estoque de acessórios"
            lancamento = Lancamento(
                data,
                f"Compra: {quantidade}x {item.nome}",
                categoria,
                custo_unitario_centavos * quantidade,
                SAIDA,
                item.id,
            )
            conexao.execute(
                "UPDATE estoque SET quantidade = ?, custo_centavos = ? WHERE id = ?",
                (item.quantidade, item.custo_centavos, item.id),
            )
            inserir_lancamento(conexao, lancamento)
        return lancamento