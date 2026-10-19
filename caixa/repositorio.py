import sqlite3
from datetime import date
from pathlib import Path

from caixa.modelos import Lancamento

SCHEMA = """
CREATE TABLE IF NOT EXISTS lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL,
    tipo TEXT NOT NULL
)
"""


class RepositorioLancamentos:
    def __init__(self, caminho_banco: str | Path):
        self.caminho_banco = caminho_banco
        self._executar(SCHEMA)

    def _executar(self, sql: str, parametros: tuple = ()) -> list:
        conexao = sqlite3.connect(self.caminho_banco)
        try:
            with conexao:  # confirma a operação se der certo, desfaz se der erro
                return conexao.execute(sql, parametros).fetchall()
        finally:
            conexao.close()

    def adicionar(self, lancamento: Lancamento) -> None:
        self._executar(
            "INSERT INTO lancamentos (data, descricao, categoria, valor_centavos, tipo) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                lancamento.data.isoformat(),
                lancamento.descricao,
                lancamento.categoria,
                lancamento.valor_centavos,
                lancamento.tipo,
            ),
        )

    def listar(self) -> list[Lancamento]:
        linhas = self._executar(
            "SELECT data, descricao, categoria, valor_centavos, tipo "
            "FROM lancamentos ORDER BY data, id"
        )
        return [
            Lancamento(date.fromisoformat(data), descricao, categoria, valor, tipo)
            for data, descricao, categoria, valor, tipo in linhas
        ]