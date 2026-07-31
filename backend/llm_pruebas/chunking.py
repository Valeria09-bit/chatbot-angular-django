from langchain_text_splitters import RecursiveCharacterTextSplitter


def dividir_en_chunks(texto, tamano_chunk=500, traslape=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=tamano_chunk,
        chunk_overlap=traslape,
        separators=["\n\n", "\n", ". ", " ", ""]  # intenta cortar en saltos de párrafo primero
    )
    chunks = splitter.split_text(texto)
    return chunks


if __name__ == "__main__":
    ruta_chunks = "../Documentos/chunks.txt"

    # Leemos el texto ya limpio (el que generó extraer_texto_final.py)
    with open(ruta_chunks, "r", encoding="utf-8") as f:
        texto = f.read()

    chunks = dividir_en_chunks(texto)

    print(f"Total de chunks generados: {len(chunks)}")
    print("\n--- Ejemplo: primer chunk ---\n")
    print(chunks[0])
    print("\n--- Ejemplo: segundo chunk ---\n")
    print(chunks[1])

    # Sobrescribimos el mismo chunks.txt, ahora ya dividido y numerado
    with open(ruta_chunks, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"=== CHUNK {i} ===\n")
            f.write(chunk)
            f.write("\n\n")

    print(f"\nChunks guardados en {ruta_chunks}")