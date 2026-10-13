import pymupdf4llm

def extraer_y_limpiar_pdf(ruta_pdf):
    print(f"Procesando {ruta_pdf} con PyMuPDF4LLM...")
    # Convierte el PDF directamente (ignorando la basura visual)
    md_text = pymupdf4llm.to_markdown(ruta_pdf)
    return md_text

if __name__ == "__main__":
    # PDF con el archivo de texto donde se va a guardar
    documentos = {
        "../Documentos/Convocatoria_MCDI_INFOTEC_2026.pdf": "../Documentos/convocatoria.txt",
        "../Documentos/FolletoMCDI.pdf": "../Documentos/folleto.txt",
    }

    for ruta_pdf, ruta_guardado in documentos.items():
        # Extraemos el texto
        texto_limpio = extraer_y_limpiar_pdf(ruta_pdf)

        # Guardamos el resultado en un archivo de texto
        with open(ruta_guardado, "w", encoding="utf-8") as f:
            f.write(texto_limpio)

        print(f"Texto extraído y guardado en {ruta_guardado}")