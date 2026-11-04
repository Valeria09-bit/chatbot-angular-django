"""
ingestar.py  -  Pipeline de ingesta para la base de conocimiento del chatbot MCDI.

Para cada PDF en backend/Documentos/:
  1. Extrae el texto con PyMuPDF4LLM (igual que llm_pruebas/pdf.py)
  2. Lo divide en chunks (por artículos si es un reglamento, por secciones
     numeradas si es una convocatoria; mismo splitter que llm_pruebas/chunking.py)
  3. Genera embeddings (paraphrase-multilingual-mpnet-base-v2)
  4. Los guarda en Chroma (colección "convocatoria_mcdi", la que leen los scripts RAG)

Uso (desde la raíz del proyecto, con el entorno virtual activo):
    python ingestar.py              # agrega/actualiza los PDF de Documentos/
    python ingestar.py --reset      # borra la colección y reconstruye todo
    python ingestar.py --solo-chunks  # no toca Chroma, solo escribe chunks_<pdf>.txt para revisar
    python ingestar.py archivo.pdf  # procesa solo ese PDF
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CARPETA_PDF = RAIZ / "backend" / "Documentos"
CARPETA_REVISION = RAIZ / "backend" / "Documentos" / "chunks_revision"
RUTA_CHROMA = str(RAIZ / "chroma_db")
COLECCION = "convocatoria_mcdi"
MODELO_EMB = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

TAM_SECCION = 1200      # documentos tipo convocatoria
TAM_ARTICULO = 1000     # documentos tipo reglamento
TRASLAPE = 100
# Encabezado de artículo; tolera "**Artículo 3** ." (negritas de markdown) y "Artículo88."
PAT_ART = r"(?m)^\W*Art[ií]culo\s*\d+[\s*]*\."
MIN_ARTICULOS = 10      # si hay al menos estos "Artículo N." se usa el modo reglamento


# ---------- 1. Extracción ----------
def extraer(ruta_pdf: Path) -> str:
    import pymupdf4llm
    texto = pymupdf4llm.to_markdown(str(ruta_pdf))
    texto = re.sub(r"-\n(\w)", r"\1", texto)     # palabras cortadas con guion al final de línea
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto


# ---------- 2. Chunking ----------
def _splitter(tam):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(
        chunk_size=tam, chunk_overlap=TRASLAPE,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunks_por_articulos(texto: str) -> list[str]:
    splitter = _splitter(TAM_ARTICULO)
    # tolera "Artículo 5.", "**Artículo 5.**", "Artículo88." (sin espacio)
    partes = re.split(r"(?m)(?=^\W*Art[ií]culo\s*\d+[\s*]*\.)", texto)
    chunks = []
    for parte in partes:
        parte = parte.strip()
        if len(parte) < 40:
            continue
        m = re.match(r"\W*(Art[ií]culo\s*\d+)", parte)
        if len(parte) <= TAM_ARTICULO:
            chunks.append(parte)
            continue
        for j, sub in enumerate(splitter.split_text(parte)):
            if j > 0 and m:    # repetir el encabezado para no perder a qué artículo pertenece
                sub = f"{m.group(1)} (continuación). {sub}"
            chunks.append(sub)
    return chunks


def chunks_por_secciones(texto: str) -> list[str]:
    splitter = _splitter(TAM_SECCION)
    # encabezados numerados en MAYÚSCULAS, con o sin '#' de markdown (p. ej. "# 5. COSTOS")
    secciones = [s.strip() for s in re.split(r"(?m)(?=^[#*\s]*\d+\.\s+[A-ZÁÉÍÓÚÑ]{3})", texto) if s.strip()]
    chunks = []
    for s in secciones:
        chunks.extend([s] if len(s) <= TAM_SECCION else splitter.split_text(s))
    return chunks


def chunkear(texto: str) -> list[str]:
    n_art = len(re.findall(PAT_ART, texto))
    if n_art >= MIN_ARTICULOS:
        return chunks_por_articulos(texto)
    return chunks_por_secciones(texto)


# ---------- 3/4. Embeddings + Chroma ----------
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    reset = "--reset" in sys.argv
    solo_chunks = "--solo-chunks" in sys.argv

    pdfs = [CARPETA_PDF / a for a in args] if args else sorted(CARPETA_PDF.glob("*.pdf"))
    if not pdfs:
        print("No hay PDFs en", CARPETA_PDF)
        return

    docs = {}
    for pdf in pdfs:
        texto = extraer(pdf)
        chunks = chunkear(texto)
        docs[pdf.stem] = chunks
        modo = "artículos" if len(re.findall(PAT_ART, texto)) >= MIN_ARTICULOS else "secciones"
        print(f"{pdf.name}: {len(texto)} caracteres -> {len(chunks)} chunks (modo {modo})")
        CARPETA_REVISION.mkdir(parents=True, exist_ok=True)
        with open(CARPETA_REVISION / f"chunks_{pdf.stem}.txt", "w", encoding="utf-8") as f:
            for i, c in enumerate(chunks):
                f.write(f"=== CHUNK {i} ===\n{c.strip()}\n\n")

    if solo_chunks:
        print("Listo. Revisa los .txt en", CARPETA_REVISION)
        return

    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=RUTA_CHROMA)
    if reset:
        try:
            client.delete_collection(COLECCION)
            print("Colección borrada.")
        except Exception:
            pass
    col = client.get_or_create_collection(COLECCION)

    modelo = SentenceTransformer(MODELO_EMB)
    modelo.max_seq_length = 384     # el default (128) recorta los chunks largos

    for nombre, chunks in docs.items():
        col.delete(where={"fuente": nombre})     # re-ejecutar actualiza, no duplica
        embs = modelo.encode(chunks, show_progress_bar=True).tolist()
        col.add(
            ids=[f"{nombre}_{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=embs,
            metadatas=[{"fuente": nombre} for _ in chunks],
        )
        print(f"{nombre}: {len(chunks)} chunks guardados.")

    print("Total en la colección:", col.count())


if __name__ == "__main__":
    main()