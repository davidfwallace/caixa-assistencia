import pytest

from app import criar_app


@pytest.fixture
def cliente(tmp_path):
    app = criar_app(tmp_path / "teste.db")
    return app.test_client()


def test_pagina_inicial_abre(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Caixa Assistência" in resposta.get_data(as_text=True)


def test_lancamento_adicionado_aparece_no_mes(cliente):
    cliente.post("/lancamentos", data={
        "data": "2026-10-03",
        "descricao": "Tela iPhone XR teste",
        "categoria": "Conserto",
        "valor": "250,00",
    })
    pagina = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "Tela iPhone XR teste" in pagina
    assert "R$ 250,00" in pagina


def test_valor_invalido_mostra_erro_e_nao_salva(cliente):
    resposta = cliente.post("/lancamentos", data={
        "data": "2026-10-03",
        "descricao": "Lançamento inválido",
        "categoria": "Conserto",
        "valor": "-5,00",
    }, follow_redirects=True)
    assert "Não foi possível salvar" in resposta.get_data(as_text=True)

    pagina_do_mes = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "Nenhum lançamento neste mês" in pagina_do_mes

def cadastrar_item(cliente, **mudancas):
    dados = {
        "peca": "Bateria", "variante": "", "modelo": "iPhone 11",
        "quantidade": "3", "custo": "89,90", "preco": "250,00", "minimo": "5",
    }
    dados.update(mudancas)
    return cliente.post("/estoque/itens", data=dados, follow_redirects=True)


def test_pagina_de_estoque_abre(cliente):
    assert cliente.get("/estoque").status_code == 200


def test_item_cadastrado_aparece_no_estoque(cliente):
    pagina = cadastrar_item(cliente, quantidade="10").get_data(as_text=True)
    assert "Bateria — iPhone 11" in pagina
    assert "cadastrado no estoque" in pagina


def test_cadastro_invalido_mostra_erro(cliente):
    pagina = cadastrar_item(cliente, variante="Frontal").get_data(as_text=True)
    assert "Não foi possível cadastrar" in pagina


def test_estoque_baixo_mostra_alerta_em_todas_as_paginas(cliente):
    cadastrar_item(cliente, quantidade="3")
    for endereco in ["/", "/estoque"]:
        pagina = cliente.get(endereco).get_data(as_text=True)
        assert "Fazer pedido ao fornecedor" in pagina
        assert "Bateria — iPhone 11 (restam 3)" in pagina


def test_compra_repoe_estoque_e_lanca_no_caixa(cliente):
    cadastrar_item(cliente, quantidade="3")
    cliente.post("/estoque/compras", data={"item_id": "1", "quantidade": "10", "custo": "90,00"})

    caixa = cliente.get("/").get_data(as_text=True)
    assert "Compra: 10x Bateria — iPhone 11" in caixa
    assert "Fazer pedido ao fornecedor" not in caixa  # agora são 13, acima do mínimo

def registrar_conserto(cliente, item_id="1", valor="250,00"):
    return cliente.post("/servicos", data={
        "item_id": item_id, "data": "2026-10-03", "valor": valor,
    }, follow_redirects=True)


def test_conserto_aparece_no_caixa(cliente):
    cadastrar_item(cliente, quantidade="10")
    registrar_conserto(cliente)
    caixa = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "Bateria — iPhone 11" in caixa
    assert "R$ 250,00" in caixa


def test_conserto_que_chega_no_minimo_dispara_alerta(cliente):
    cadastrar_item(cliente, quantidade="6")
    assert "Fazer pedido ao fornecedor" not in cliente.get("/").get_data(as_text=True)

    registrar_conserto(cliente)

    pagina = cliente.get("/").get_data(as_text=True)
    assert "Bateria — iPhone 11 (restam 5)" in pagina


def test_conserto_sem_estoque_mostra_erro(cliente):
    cadastrar_item(cliente, quantidade="0")
    pagina = registrar_conserto(cliente).get_data(as_text=True)
    assert "Não foi possível registrar" in pagina


def test_lucro_do_conserto_aparece_no_caixa(cliente):
    cadastrar_item(cliente, quantidade="10")   # custo de R$ 89,90
    registrar_conserto(cliente)                # cobrado R$ 250,00
    caixa = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "Lucro bruto" in caixa
    assert "R$ 160,10" in caixa


def test_avulso_com_custo_mostra_o_lucro(cliente):
    cliente.post("/lancamentos", data={
        "data": "2026-10-03",
        "descricao": "Tela Apple Watch teste",
        "categoria": "Conserto",
        "valor": "350,00",
        "custo": "200,00",
    })
    pagina = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "R$ 150,00" in pagina


def test_cadastro_com_quantidade_lanca_a_compra_no_caixa(cliente):
    cadastrar_item(cliente, quantidade="10")
    caixa = cliente.get("/").get_data(as_text=True)
    assert "Compra: 10x Bateria — iPhone 11" in caixa


def test_cadastro_sem_quantidade_nao_mexe_no_caixa(cliente):
    cadastrar_item(cliente, quantidade="0")
    caixa = cliente.get("/").get_data(as_text=True)
    assert "Nenhum lançamento neste mês" in caixa


def test_perda_reduz_o_lucro_do_mes(cliente):
    cadastrar_item(cliente, quantidade="10")   # custo de R$ 89,90
    registrar_conserto(cliente)                # R$ 250,00 em 03/10/2026
    cliente.post("/estoque/perdas", data={
        "item_id": "1", "quantidade": "1", "motivo": "Troca em garantia", "data": "2026-10-05",
    })
    pagina = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "R$ 70,20" in pagina                # 250,00 − 89,90 − 89,90
    assert "Troca em garantia" in pagina