import pdfplumber
import re

def limpiar_texto(texto):
    """Limpia el ruido visual y textos corruptos del PDF de INFOTEC."""
    if not texto:
        return ""
    
    # Lista de frases de diseño/publicitarias que se cruzan en el PDF
    frases_basura = [
        r'Constancia de participación al finalizar el curso',
        r'Acceso a materiales y ejercicios prácticos',
        r'Desarrollo de habilidades críticas para proyectos reales',
        r'Los ogr mas e Técn Supe Un e it e TEC o de',
        r'nve gación e In c en T a fo ón mun n \(en',
        r'ela te “INFOTE , tie opó form pr ona i de',
        r'qu nes han co uido d ivel io s'
    ]
    
    # Eliminar las frases del margen
    for frase in frases_basura:
        texto = re.sub(frase, '', texto, flags=re.IGNORECASE)
    
    # Limpiar espacios y saltos de línea excesivos que deja la eliminación
    texto = re.sub(r' {2,}', ' ', texto) # Quita dobles espacios
    texto = re.sub(r'\n{2,}', '\n', texto) # Quita saltos de línea dobles
    
    return texto.strip()

def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages, start=1):
            texto_crudo = pagina.extract_text()
            
            if texto_crudo:
                # 1. Limpiamos el texto antes de sumarlo
                texto_limpio = limpiar_texto(texto_crudo)
                
                # 2. Ya NO inyectamos el "--- Página X ---" para no confundir al RAG
                texto_completo += texto_limpio + "\n\n"
            else:
                print(f"Aviso: la página {numero_pagina} no tiene texto extraíble")
                
    return texto_completo


if __name__ == "__main__":
    ruta = "../Documentos/Convocatoria_MCDI_INFOTEC_2026.pdf"
    texto = extraer_texto_pdf(ruta)
    
    print(f"Total de caracteres extraídos: {len(texto)}")
    print("\n--- Primeros 500 caracteres ---\n")
    print(texto[:500])
    
    # Al guardarlo, este txt estará listo para tu text_splitter
    with open("../Documentos/chunks.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print("\nTexto guardado en Documentos/chunks.txt")