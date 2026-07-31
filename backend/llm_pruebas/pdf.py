import pdfplumber
import re

# Frases de "ruido" (banner lateral) que se repiten completas en cada página
FRASES_BASURA = [
    r'Constancia de participación al finalizar el curso',
    r'Acceso a materiales y ejercicios prácticos',
    r'Desarrollo de habilidades críticas para proyectos reales',
    r'Los ogr mas e Técn Supe Un e it e TEC o de',
    r'nve gación e In c en T a fo ón mun n \(en',
    r'ela te \u201cINFOTE , tie opó form pr ona i de',
    r'qu nes han co uido d ivel io s',
]

# Líneas donde el ruido quedó entreverado letra por letra con el texto real.
# Se reconstruyeron separando los caracteres del PDF por su altura (top) exacta,
# ya que las dos capas de texto están escritas a una fracción de punto de
# diferencia una de otra (imposible de separar con regex normal).
LINEAS_CORRUPTAS = {
    "programDeas daerr oplolos gdrea dhaob: ilidades críticas para proyectos reales":
        "programa de posgrado:",
    "2.1 RCeoqnustiasnictioa sd e gpaernticeipraacilóen sa:l finalizar el curso":
        "2.1 Requisitos generales:",
    "obtengaD uens paorrrocellnot adjee hfainbailli dmaíndiemso c dríeti c7a0s% peanr aco pnrjounyetoc.t os reales":
        "obtenga un porcentaje final mínimo de 70% en conjunto.",
    "ela te3 \u201c.I1N.2F OEnTvEi a r ,la t ideo cument ació on pmóe ncion afdoar mde l puntop r2 .1. ona i de":
        "3.1.2 Enviar la documentación mencionada del punto 2.1.",
    "CoDnosctuamnceinat adcei ópna rqtiuceip saec ipórne sael nfitnea ilnizcaorm epl lceutars, oa lterada, o recibida de forma":
        "Documentación que se presente incompleta, alterada, o recibida de forma",
    "DIensfaorrrmoallcoi ódne qhuaeb inliod aedsetés cdreítbiicdaasm peanrtae pcraopyteucrtaodsa ree ailnetse grada en el Sistema":
        "Información que no esté debidamente capturada e integrada en el Sistema",
}


def limpiar_texto(texto):
    """Limpia el ruido visual y corrige las líneas corruptas del PDF de INFOTEC."""
    if not texto:
        return ""

    # 1) Quitar las frases de banner que aparecen completas
    for frase in FRASES_BASURA:
        texto = re.sub(frase, '', texto, flags=re.IGNORECASE)

    # 2) Reemplazar las líneas mezcladas letra por letra por su versión correcta
    for corrupta, correcta in LINEAS_CORRUPTAS.items():
        texto = texto.replace(corrupta, correcta)

    # 3) Limpiar espacios y saltos de línea excesivos que deja la limpieza
    texto = re.sub(r' {2,}', ' ', texto)
    texto = re.sub(r'\n{2,}', '\n', texto)

    return texto.strip()


def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages, start=1):
            texto_crudo = pagina.extract_text()

            if texto_crudo:
                texto_limpio = limpiar_texto(texto_crudo)
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

    with open("../Documentos/chunks.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print("\nTexto guardado en Documentos/chunks.txt")