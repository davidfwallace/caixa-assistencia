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