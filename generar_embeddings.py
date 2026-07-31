"""
Script: generar_embeddings.py
Objetivo: leer chunks.txt, generar embeddings y guardarlos en ChromaDB
para el chatbot RAG de INFOTEC (MCDI).

Instalar dependencias (dentro del venv 'backend'):
    pip install sentence-transformers chromadb
"""

import re
import chromadb
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------
# 1. Leer y separar los chunks del archivo chunks.txt
# ------------------------------------------------------------------
def leer_chunks(ruta_archivo: str) -> list[str]:
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # separa por las marcas "=== CHUNK N ==="
    partes = re.split(r"=== CHUNK \d+ ===", contenido)
    # quita espacios y elimina chunks vacíos
    chunks = [p.strip() for p in partes if p.strip()]
    return chunks


# ------------------------------------------------------------------
# 2. Generar embeddings con un modelo multilingüe
# ------------------------------------------------------------------
def generar_embeddings(chunks: list[str]):
    modelo = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )
    embeddings = modelo.encode(chunks, show_progress_bar=True)
    return embeddings, modelo


# ------------------------------------------------------------------
# 3. Guardar en ChromaDB (persistente en disco)
# ------------------------------------------------------------------
def guardar_en_chroma(chunks: list[str], embeddings, ruta_db="./chroma_db"):
    client = chromadb.PersistentClient(path=ruta_db)

    coleccion = client.get_or_create_collection(
        name="convocatoria_mcdi",
        metadata={"descripcion": "Chunks de la convocatoria MCDI INFOTEC 2026-2"},
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    coleccion.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
    )

    print(f"Se guardaron {len(chunks)} chunks en la colección 'convocatoria_mcdi'.")
    return coleccion


# ------------------------------------------------------------------
# 4. Función de prueba: recuperar los chunks más relevantes
# ------------------------------------------------------------------
def recuperar_contexto(pregunta: str, modelo, ruta_db="./chroma_db", n_resultados=3):
    client = chromadb.PersistentClient(path=ruta_db)
    coleccion = client.get_collection("convocatoria_mcdi")

    embedding_pregunta = modelo.encode([pregunta]).tolist()

    resultados = coleccion.query(
        query_embeddings=embedding_pregunta,
        n_results=n_resultados,
    )

    return resultados["documents"][0]


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    RUTA_CHUNKS = "chunks.txt"  # ajusta la ruta según dónde lo tengas

    print("Leyendo chunks...")
    chunks = leer_chunks(RUTA_CHUNKS)
    print(f"Se encontraron {len(chunks)} chunks.")

    print("Generando embeddings...")
    embeddings, modelo = generar_embeddings(chunks)

    print("Guardando en ChromaDB...")
    guardar_en_chroma(chunks, embeddings)

    # Prueba rápida
    pregunta_prueba = "¿Cuánto cuesta el examen de admisión?"
    contexto = recuperar_contexto(pregunta_prueba, modelo)
    print("\n--- Prueba de recuperación ---")
    print(f"Pregunta: {pregunta_prueba}")
    for i, c in enumerate(contexto, 1):
        print(f"\nResultado {i}:\n{c[:200]}...")