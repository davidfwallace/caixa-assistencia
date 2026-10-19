# Caixa Assistência

![Testes](https://github.com/davidfwallace/caixa-assistencia/actions/workflows/testes.yml/badge.svg)

Controle de caixa para uma pequena assistência técnica de iPhones: consertos (bateria, tela, microfone), venda de aparelhos seminovos e venda de acessórios (películas e capinhas).

Projeto pessoal criado para praticar engenharia de software: separação de responsabilidades, testes automatizados e integração contínua.

Interface web:

```bash
python app.py
```

Acesse http://127.0.0.1:5001

## Funcionalidades

- Registro de lançamentos de entrada e saída, com data, descrição, categoria e valor
- Validação dos dados na criação (valor positivo, categoria compatível com o tipo, descrição obrigatória)
- Filtro de lançamentos por mês
- Resumo do mês: total de entradas, total de saídas, saldo e totais por categoria
- Conversão e formatação de valores no padrão brasileiro (`R$ 1.299,90`)

**Categorias**

| Entradas | Saídas |
|---|---|
| Conserto | Peças |
| Venda de seminovo | Compra de aparelho |
| Venda de acessório | Estoque de acessórios |
| | Despesas fixas |

## Decisões de projeto

- **Dinheiro em centavos inteiros.** Valores são guardados como `int` (R$ 49,90 → `4990`), nunca como `float`. Em ponto flutuante, `0.1 + 0.2` resulta em `0.30000000000000004`, um erro inaceitável num caixa. Há um teste que documenta esse problema e a solução.
- **Validação no modelo.** O `Lancamento` valida seus dados ao ser criado (`__post_init__`), então um lançamento inválido nunca chega a existir no sistema.
- **Valores sempre positivos.** Se o dinheiro entrou ou saiu é definido pelo campo `tipo`, e não pelo sinal do valor, evitando ambiguidade.
- **Formato brasileiro explícito.** A entrada `49.90` é recusada por ser ambígua no padrão brasileiro (o ponto é separador de milhar). O correto é `49,90`.
- **Responsabilidades separadas.** Conversão de valores, modelo de dados e cálculos ficam em módulos diferentes, o que facilita testar cada parte isoladamente.

## Estrutura

```
caixa-assistencia/
├── caixa/
│   ├── dinheiro.py   # conversão e formatação de valores
│   ├── modelos.py    # modelo de lançamento e categorias
│   └── calculos.py   # saldo, totais e filtros
├── tests/            # testes automatizados (pytest)
├── demo.py           # demonstração com dados fictícios
└── .github/workflows/testes.yml   # CI com GitHub Actions
```

## Como rodar

Requer Python 3.12 ou superior.

```bash
git clone https://github.com/davidfwallace/caixa-assistencia.git
cd caixa-assistencia
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Demonstração com dados fictícios:

```bash
python demo.py
```

Testes:

```bash
pytest -v
```

## Testes e integração contínua

O projeto tem 31 testes automatizados, com atenção especial a casos de borda: limites de mês, valores negativos, formatos inválidos e saldo negativo. A cada push, o GitHub Actions roda toda a suíte de testes em Python 3.12, 3.13 e 3.14.

## Próximos passos

- [x] Interface web com Flask
- [x] Persistência dos lançamentos em banco de dados (SQLite)
- [ ] Importação de lançamentos a partir de CSV
- [ ] v2: rastrear o lucro por aparelho (compra de aparelho com defeito → peças → revenda)

## Uso de IA

Este projeto foi desenvolvido com o auxílio do Claude como tutor. A IA sugeriu a estrutura básica do projeto, explicou os conceitos envolvidos (pacotes, dataclasses, pytest, CI) e gerou a primeira versão do código. Eu revisei e executei cada parte, investiguei os erros que apareceram e garanti que entendo cada decisão.

Um exemplo: um dos testes originalmente assumia que `sum([0.1] * 10)` retornava um valor impreciso, mas a partir do Python 3.12 a função `sum()` passou a compensar erros de arredondamento. O teste falhou, investigamos a causa e ele foi reescrito para demonstrar o problema com uma soma direta (`0.1 + 0.2`).

## Autor

João Gustavo G. Pires — Eng. da Computação, CIn - UFPE