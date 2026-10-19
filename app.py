from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from caixa.calculos import filtrar_por_mes, saldo, total_por_categoria, total_por_tipo
from caixa.dinheiro import formatar_reais, reais_para_centavos
from caixa.modelos import CATEGORIAS, ENTRADA, SAIDA, Lancamento
from caixa.repositorio import RepositorioLancamentos

# {"Conserto": "entrada", "Peças": "saida", ...}
TIPO_DA_CATEGORIA = {
    categoria: tipo for tipo, categorias in CATEGORIAS.items() for categoria in categorias
}


def criar_app(caminho_banco="caixa.db"):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"  # necessário pro flash; só para uso local
    app.jinja_env.filters["reais"] = formatar_reais
    repo = RepositorioLancamentos(caminho_banco)

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
            flash(f"Não foi possível salvar: {erro}")
            return redirect(url_for("index"))

        repo.adicionar(lancamento)
        return redirect(url_for("index", mes=lancamento.data.strftime("%Y-%m")))

    return app


if __name__ == "__main__":
    criar_app().run(debug=True, port=5001)