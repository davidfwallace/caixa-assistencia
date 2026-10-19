from datetime import date
from pathlib import Path

from caixa.banco import abrir, inicializar
from caixa.modelos import Lancamento


def inserir_lancamento(conexao, lancamento: Lancamento) -> None:
    conexao.execute(
        "INSERT INTO lancamentos (data, descricao, categoria, valor_centavos, tipo, item_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            lancamento.data.isoformat(),
            lancamento.descricao,
            lancamento.categoria,
            lancamento.valor_centavos,
            lancamento.tipo,
            lancamento.item_id,
        ),
    )


class RepositorioLancamentos:
    def __init__(self, caminho_banco: str | Path):
        self.caminho_banco = caminho_banco
        inicializar(caminho_banco)

    def adicionar(self, lancamento: Lancamento) -> None:
        with abrir(self.caminho_banco) as conexao:
            inserir_lancamento(conexao, lancamento)

    def listar(self) -> list[Lancamento]:
        with abrir(self.caminho_banco) as conexao:
            linhas = conexao.execute(
                "SELECT data, descricao, categoria, valor_centavos, tipo, item_id "
                "FROM lancamentos ORDER BY data, id"
            ).fetchall()
        return [
            Lancamento(date.fromisoformat(data), descricao, categoria, valor, tipo, item_id)
            for data, descricao, categoria, valor, tipo, item_id in linhas
        ]