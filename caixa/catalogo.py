SERVICOS = {
    "Tela": ["Frontal", "Traseira"],
    "Bateria": [],
    "Câmera": ["Principal", "Ultra-angular", "Zoom", "Frontal"],
    "Microfone": [],
    "Conector de carga": [],
}

ACESSORIOS = {
    "Película": ["Vidro 3D", "Privacidade", "Hidrogel"],
    "Capinha": ["Silicone", "Transparente", "Anti-impacto"],
}

# Peças e acessórios juntos: tudo que pode existir no estoque
PECAS = {**SERVICOS, **ACESSORIOS}

MODELOS = [
    "iPhone XR",
    "iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
    "iPhone 12", "iPhone 12 mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
]