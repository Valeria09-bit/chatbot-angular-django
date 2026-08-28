import pymupdf4llm

def extraer_y_limpiar_pdf(ruta_pdf):
    print(f"Procesando {ruta_pdf} con PyMuPDF4LLM...")
    # Convierte el PDF directamente a Markdown estructurado (ignora la basura visual)
    md_text = pymupdf4llm.to_markdown(ruta_pdf)
    return md_text

if __name__ == "__main__":
    # ruta
    ruta = "../Documentos/Convocatoria_MCDI_INFOTEC_2026.pdf"
    
    # Extraemos el texto
    texto_limpio = extraer_y_limpiar_pdf(ruta)
    
    # Guardamos el resultado en un archivo .md
    ruta_guardado = "../Documentos/convocatoria.txt"
    with open(ruta_guardado, "w", encoding="utf-8") as f:
        f.write(texto_limpio)
        
    print(f"¡Éxito! Texto extraído y guardado impecablemente en {ruta_guardado}")