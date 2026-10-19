def reais_para_centavos(texto: str) -> int:
    """Converte '1.299,90' (formato brasileiro) em 129990 centavos."""
    texto = texto.strip().replace("R$", "").strip()

    if texto.startswith("-"):
        raise ValueError("O valor não pode ser negativo.")

    if "," in texto:
        # Com vírgula, os pontos são separadores de milhar: '1.299,90'
        inteiro, decimal = texto.replace(".", "").split(",")
    elif "." in texto:
        # '49.90' é ambíguo no Brasil, então recusamos
        raise ValueError("Use vírgula para os centavos, ex.: 49,90")
    else:
        inteiro, decimal = texto, "0"

    if len(decimal) > 2:
        raise ValueError("Use no máximo 2 casas decimais.")

    decimal = decimal.ljust(2, "0")  # '9' vira '90'
    return int(inteiro) * 100 + int(decimal)


def formatar_reais(centavos: int) -> str:
    """Converte 129990 em 'R$ 1.299,90'."""
    sinal = "-" if centavos < 0 else ""
    reais, cent = divmod(abs(centavos), 100)
    reais_formatado = f"{reais:,}".replace(",", ".")
    return f"{sinal}R$ {reais_formatado},{cent:02d}"