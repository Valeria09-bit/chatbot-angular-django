import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ------------------------------------------------------------
# 1. Separar el documento por secciones
# ------------------------------------------------------------
def separar_por_secciones(texto):
    """
    Divide el documento utilizando encabezados numerados,
    por ejemplo:

    1. ...
    2. ...
    3. ...
    4. CALENDARIO DE ACTIVIDADES
    5. COSTOS
    6. MOTIVOS PARA ANULAR SOLICITUDES
    """

    patron = r"(?m)(?=^\s*\d+\.\s+)"

    secciones = re.split(patron, texto)

    # Limpiar espacios y eliminar elementos vacíos
    secciones = [
        seccion.strip()
        for seccion in secciones
        if seccion.strip()
    ]

    return secciones


# ------------------------------------------------------------
# 2. Dividir las secciones demasiado grandes
# ------------------------------------------------------------
def dividir_texto_en_chunks(texto, tamano=1200, traslape=100):

    secciones = separar_por_secciones(texto)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=tamano,
        chunk_overlap=traslape,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks_finales = []

    for seccion in secciones:

        # Si la sección cabe completa, conservarla completa
        if len(seccion) <= tamano:
            chunks_finales.append(seccion)

        # Si es demasiado grande, dividirla
        else:
            chunks_seccion = splitter.split_text(seccion)
            chunks_finales.extend(chunks_seccion)

    return chunks_finales


# ------------------------------------------------------------
# 3. Programa principal
# ------------------------------------------------------------
if __name__ == "__main__":

    # Leer la extracción del PDF
    with open("../Documentos/convocatoria.txt", "r", encoding="utf-8") as f:
        texto_puro = f.read()

    # Generar chunks
    chunks = dividir_texto_en_chunks(texto_puro)

    print(f"Total de chunks generados: {len(chunks)}")

    # Guardar/reemplazar chunks.txt
    with open("../chunks.txt", "w", encoding="utf-8") as f:

        for i, chunk in enumerate(chunks):

            f.write(f"=== CHUNK {i} ===\n")
            f.write(chunk.strip())
            f.write("\n\n")

    print("chunks.txt actualizado correctamente.")

    # Mostrar todos los chunks
    for i, chunk in enumerate(chunks):

        print(f"\n=== CHUNK {i} ===")
        print(chunk)