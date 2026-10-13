import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def separar_por_secciones(texto):
    
    patron = r"(?m)(?=^\s*\d+\.\s+)"

    secciones = re.split(patron, texto)

    # Limpiar espacios y eliminar elementos vacíos
    secciones = [
        seccion.strip()
        for seccion in secciones
        if seccion.strip()
    ]

    return secciones


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


if __name__ == "__main__":

    # Leer la extracción del folleto
    with open("../Documentos/folleto.txt", "r", encoding="utf-8") as f:
        texto_puro = f.read()

    # Generar chunks
    chunks = dividir_texto_en_chunks(texto_puro)

    print(f"Total de chunks generados: {len(chunks)}")

    # Guardar el archivo de folleto para no mezclarla con la convocatoria
    with open("../chunks_folleto.txt", "w", encoding="utf-8") as f:

        for i, chunk in enumerate(chunks):

            f.write(f"=== CHUNK {i} ===\n")
            f.write(chunk.strip())
            f.write("\n\n")

    print("chunks_folleto.txt creado correctamente.")

    # Mostrar todos los chunks
    for i, chunk in enumerate(chunks):

        print(f"\n=== CHUNK {i} ===")
        print(chunk)