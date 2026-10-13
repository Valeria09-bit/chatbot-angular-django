import re
import chromadb
from sentence_transformers import SentenceTransformer

# Lee y separa los chunks del archivo chunks.txt

def leer_chunks(ruta_archivo: str) -> list[str]:
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # separa las marcas " CHUNK N "
    partes = re.split(r"=== CHUNK \d+ ===", contenido)
    # quita espacios y elimina chunks vacíos
    chunks = [p.strip() for p in partes if p.strip()]
    return chunks


# Genera embeddings con el modelo multilingüe

def generar_embeddings(chunks: list[str]):
    modelo = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )
    embeddings = modelo.encode(chunks, show_progress_bar=True)
    return embeddings, modelo



#  Guardar en ChromaDB  

def guardar_en_chroma(chunks: list[str], embeddings, prefijo="chunk", fuente="convocatoria", ruta_db="./chroma_db"):
    client = chromadb.PersistentClient(path=ruta_db)

    coleccion = client.get_or_create_collection(
        name="convocatoria_mcdi",
        metadata={"descripcion": "Chunks de la convocatoria MCDI INFOTEC 2026-2"},
    )

    # el prefijo evita que los IDs de un documento choquen 
    ids = [f"{prefijo}_{i}" for i in range(len(chunks))]
    # guarda de qué documento viene cada chunk
    metadatas = [{"fuente": fuente} for _ in chunks]

    coleccion.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(f"Se guardaron {len(chunks)} chunks de '{fuente}' en la colección 'convocatoria_mcdi'.")
    return coleccion


# Función de prueba: recuperar los chunks más relevantes

def recuperar_contexto(pregunta: str, modelo, ruta_db="./chroma_db", n_resultados=3):
    client = chromadb.PersistentClient(path=ruta_db)
    coleccion = client.get_collection("convocatoria_mcdi")

    embedding_pregunta = modelo.encode([pregunta]).tolist()

    resultados = coleccion.query(
        query_embeddings=embedding_pregunta,
        n_results=n_resultados,
    )

    return resultados["documents"][0]




if __name__ == "__main__":
    RUTA_CHUNKS = "backend/chunks_folleto.txt"  # ajusta la ruta según dónde este
    print("Leyendo chunks...")
    chunks = leer_chunks(RUTA_CHUNKS)
    print(f"Se encontraron {len(chunks)} chunks.")

    print("Generando embeddings...")
    embeddings, modelo = generar_embeddings(chunks)

    print("Guardando en ChromaDB...")
    guardar_en_chroma(chunks, embeddings, prefijo="folleto", fuente="folleto")

    # Prueba rápida
    pregunta_prueba = "¿Cuáles son las materias optativas de la maestría?"
    contexto = recuperar_contexto(pregunta_prueba, modelo)

    print("\n--- RESULTADOS DE LA BÚSQUEDA EN CHROMA ---")
    for i, chunk in enumerate(contexto):
        print(f"\n[Resultado {i+1}]:")
        print(chunk)