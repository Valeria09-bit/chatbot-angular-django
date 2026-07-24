import pdfplumber

def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if texto:
                texto_completo += f"\n--- Página {numero_pagina} ---\n"
                texto_completo += texto + "\n"
            else:
                print(f"Aviso: la página {numero_pagina} no tiene texto extraíble")
    return texto_completo


if __name__ == "__main__":
    ruta = "../Documentos/Convocatoria_MCDI_INFOTEC_2026.pdf"
    texto = extraer_texto_pdf(ruta)
    
    print(f"Total de caracteres extraídos: {len(texto)}")
    print("\n--- Primeros 500 caracteres ---\n")
    print(texto[:500])
    
    with open("../Documentos/convocatoria_texto.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print("\nTexto guardado en Documentos/convocatoria_texto.txt")