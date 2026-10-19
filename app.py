from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from caixa.calculos import filtrar_por_mes, saldo, total_por_categoria, total_por_tipo
from caixa.dinheiro import formatar_reais, reais_para_centavos
from caixa.modelos import CATEGORIAS, ENTRADA, SAIDA, Lancamento
from caixa.repositorio import RepositorioLancamentos
from caixa.catalogo import ACESSORIOS, MODELOS, PECAS, SERVICOS
from caixa.estoque import ItemEstoque, gerar_pedido, itens_para_repor
from caixa.repositorio_estoque import RepositorioEstoque

# {"Conserto": "entrada", "Peças": "saida", ...}
TIPO_DA_CATEGORIA = {
    categoria: tipo for tipo, categorias in CATEGORIAS.items() for categoria in categorias
}


def criar_app(caminho_banco="caixa.db"):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"  # necessário pro flash; só para uso local
    app.jinja_env.filters["reais"] = formatar_reais
    repo = RepositorioLancamentos(caminho_banco)
    repo_estoque = RepositorioEstoque(caminho_banco)

    @app.context_processor
    def injetar_alertas():
        return {"alertas": itens_para_repor(repo_estoque.listar())}

    @app.get("/")
    def index():
        hoje = date.today()
        mes_texto = request.args.get("mes", hoje.strftime("%Y-%m"))
        try:
            ano, mes = (int(parte) for parte in mes_texto.split("-"))
        except ValueError:
            ano, mes = hoje.year, hoje.month
            mes_texto = hoje.strftime("%Y-%m")

        do_mes = filtrar_por_mes(repo.listar(), ano, mes)
        return render_template(
            "index.html",
            mes_texto=mes_texto,
            lancamentos=do_mes,
            entradas=total_por_tipo(do_mes, ENTRADA),
            saidas=total_por_tipo(do_mes, SAIDA),
            saldo=saldo(do_mes),
            por_categoria=total_por_categoria(do_mes),
            categorias=CATEGORIAS,
            hoje=hoje.isoformat(),
        )

    @app.post("/lancamentos")
    def adicionar():
        formulario = request.form
        categoria = formulario.get("categoria", "")
        try:
            lancamento = Lancamento(
                data=date.fromisoformat(formulario.get("data", "")),
                descricao=formulario.get("descricao", ""),
                categoria=categoria,
                valor_centavos=reais_para_centavos(formulario.get("valor", "")),
                tipo=TIPO_DA_CATEGORIA.get(categoria, ""),
            )
        except ValueError as erro:
            flash(f"Não foi possível salvar: {erro}", "erro")
            return redirect(url_for("index"))

        repo.adicionar(lancamento)
        return redirect(url_for("index", mes=lancamento.data.strftime("%Y-%m")))

    @app.get("/estoque")
    def estoque():
        itens = repo_estoque.listar()
        return render_template(
            "estoque.html",
            itens=itens,
            pedido=gerar_pedido(itens),
            servicos=SERVICOS,
            acessorios=ACESSORIOS,
            pecas=PECAS,
            modelos=MODELOS,
        )

    @app.post("/estoque/itens")
    def cadastrar_item():
        formulario = request.form
        try:
            item = ItemEstoque(
                peca=formulario.get("peca", ""),
                variante=formulario.get("variante", ""),
                modelo=formulario.get("modelo", ""),
                quantidade=int(formulario.get("quantidade", "")),
                custo_centavos=reais_para_centavos(formulario.get("custo", "")),
                preco_centavos=reais_para_centavos(formulario.get("preco", "")),
                minimo=int(formulario.get("minimo", "")),
            )
            repo_estoque.adicionar_item(item)
        except ValueError as erro:
            flash(f"Não foi possível cadastrar: {erro}", "erro")
        else:
            flash(f"{item.nome} cadastrado no estoque.", "sucesso")
        return redirect(url_for("estoque"))

    @app.post("/estoque/compras")
    def registrar_compra():
        formulario = request.form
        try:
            lancamento = repo_estoque.registrar_compra(
                item_id=int(formulario.get("item_id", "")),
                quantidade=int(formulario.get("quantidade", "")),
                custo_unitario_centavos=reais_para_centavos(formulario.get("custo", "")),
                data=date.today(),
            )
        except ValueError as erro:
            flash(f"Não foi possível registrar a compra: {erro}", "erro")
        else:
            flash(f"{lancamento.descricao} registrada no caixa.", "sucesso")
        return redirect(url_for("estoque"))

    return app


if __name__ == "__main__":
    criar_app().run(debug=True, port=5001)