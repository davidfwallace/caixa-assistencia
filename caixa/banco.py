import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peca TEXT NOT NULL,
    variante TEXT NOT NULL,
    modelo TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    custo_centavos INTEGER NOT NULL,
    preco_centavos INTEGER NOT NULL,
    minimo INTEGER NOT NULL,
    UNIQUE (peca, variante, modelo)
);

CREATE TABLE IF NOT EXISTS lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    item_id INTEGER REFERENCES estoque(id),
    custo_centavos INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS perdas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    item_id INTEGER NOT NULL REFERENCES estoque(id),
    descricao TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    custo_unitario_centavos INTEGER NOT NULL,
    motivo TEXT NOT NULL
);
"""


@contextmanager
def abrir(caminho_banco):
    """Abre uma conexão como transação: confirma se der certo, desfaz se der erro."""
    conexao = sqlite3.connect(caminho_banco)
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()


# Colunas adicionadas depois da primeira versão do banco (migrações)
COLUNAS_NOVAS = {
    "item_id": "INTEGER REFERENCES estoque(id)",
    "custo_centavos": "INTEGER NOT NULL DEFAULT 0",
}


def inicializar(caminho_banco):
    """Cria as tabelas e atualiza bancos antigos (migração)."""
    with abrir(caminho_banco) as conexao:
        conexao.executescript(SCHEMA)
        colunas = [coluna[1] for coluna in conexao.execute("PRAGMA table_info(lancamentos)")]
        for nome, definicao in COLUNAS_NOVAS.items():
            if nome not in colunas:
                conexao.execute(f"ALTER TABLE lancamentos ADD COLUMN {nome} {definicao}")