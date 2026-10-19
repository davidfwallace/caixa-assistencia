function preencherSubcategorias(seletorPeca, seletorVariante, pecas) {
  const variantes = pecas[seletorPeca.value];
  seletorVariante.innerHTML = "";

  if (variantes.length === 0) {
    seletorVariante.add(new Option("Padrão", ""));
  } else {
    for (const variante of variantes) {
      seletorVariante.add(new Option(variante, variante));
    }
  }
}