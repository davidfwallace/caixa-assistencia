from datetime import date

from caixa.calculos import filtrar_por_mes, saldo, total_por_categoria, total_por_tipo
from caixa.dinheiro import formatar_reais, reais_para_centavos
from caixa.modelos import ENTRADA, SAIDA, Lancamento

lancamentos = [
    Lancamento(date(2026, 10, 3), "Troca de bateria iPhone 11", "Conserto", reais_para_centavos("250,00"), ENTRADA),
    Lancamento(date(2026, 10, 3), "Bateria iPhone 11", "Peças", reais_para_centavos("89,90"), SAIDA),
    Lancamento(date(2026, 10, 5), "Película 3D", "Venda de acessório", reais_para_centavos("30"), ENTRADA),
    Lancamento(date(2026, 10, 10), "iPhone 12 seminovo", "Venda de seminovo", reais_para_centavos("1.899,00"), ENTRADA),
    Lancamento(date(2026, 10, 15), "Aluguel do ponto", "Despesas fixas", reais_para_centavos("600,00"), SAIDA),
    Lancamento(date(2026, 9, 28), "Troca de tela iPhone XR", "Conserto", reais_para_centavos("320,00"), ENTRADA),
]

outubro = filtrar_por_mes(lancamentos, 2026, 10)

print("=== Resumo de outubro/2026 ===")
print("Entradas:", formatar_reais(total_por_tipo(outubro, ENTRADA)))
print("Saídas:  ", formatar_reais(total_por_tipo(outubro, SAIDA)))
print("Saldo:   ", formatar_reais(saldo(outubro)))
print()
for categoria, total in total_por_categoria(outubro).items():
    print(f"{categoria}: {formatar_reais(total)}")