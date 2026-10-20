import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

RAIZ = Path(__file__).resolve().parent.parent.parent      
RUTA_FOLLETO = RAIZ / "backend" / "Documentos" / "folleto.txt"
RUTA_SALIDA = RAIZ / "chunks_folleto.txt"

PREFIJO = "[Folleto MCDI] Maestría en Ciencia de Datos e Información"
TAMANO = 1500      # una sección que cabe completa queda como un solo chunk
TRASLAPE = 150


PLAN_ESTUDIOS_TEXTO = (
    "El plan de estudios de la MCDI se cursa en 4 semestres e incluye las siguientes asignaturas: "
    "Matemáticas; Estadística y visualización; Manejo y procesamiento de la información; "
    "Análisis de algoritmos; Optimización; Aprendizaje supervisado; Aprendizaje no supervisado; "
    "Procesamiento de lenguaje natural; Procesamiento digital de imágenes; Seminario de proyecto I; "
    "Seminario de proyecto II; Optativa I; Optativa II; y Proyecto terminal."
)


def limpiar(texto: str) -> str:
    # (tabla del plan de estudios mal extraída)
    texto = re.sub(r"<!-- Start of picture text -->.*?<!-- End of picture text -->",
                   PLAN_ESTUDIOS_TEXTO, texto, flags=re.S)
    # pie de página repetidos
    texto = re.sub(r"(?m)^.*Convocatoria Posgrados.*$", "", texto)
    # negritas y cursivas de markdown
    texto = texto.replace("**", "")
    texto = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", texto)
    #  (#### Asignaturas optativas) 
    texto = re.sub(r"(?m)^#{4,}\s+(.+?)\s*$", r"\1:", texto)
    # viñetas
    for inicio in ("Implementar tecnologías", "Analizar datos, a partir"):
        texto = re.sub(rf"(?m)^{inicio}", f"- {inicio}", texto)
    # espacios
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def separar_por_secciones(texto: str):
    """Corta en cada encabezado markdown de nivel 1 a 3 (#, ##, ###). Devuelve [(titulo, cuerpo)]."""
    patron = r"(?m)^#{1,3}\s+(.+)$"
    marcas = list(re.finditer(patron, texto))
    secciones = []
    for i, m in enumerate(marcas):
        inicio = m.end()
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        titulo = m.group(1).strip()
        cuerpo = texto[inicio:fin].strip()
        if cuerpo:                       
            secciones.append((titulo, cuerpo))
    return secciones


def generar_chunks(texto: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=TAMANO,
        chunk_overlap=TRASLAPE,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for titulo, cuerpo in separar_por_secciones(texto):
        partes = [cuerpo] if len(cuerpo) <= TAMANO else splitter.split_text(cuerpo)
        for parte in partes:
            chunks.append(f"{PREFIJO} - {titulo}\n\n{parte.strip()}")
    return chunks


if __name__ == "__main__":
    texto = limpiar(RUTA_FOLLETO.read_text(encoding="utf-8"))
    chunks = generar_chunks(texto)
    print(f"Total de chunks del folleto: {len(chunks)}")

    with open(RUTA_SALIDA, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"=== CHUNK {i} ===\n{chunk}\n\n")
    print(f"Guardado en {RUTA_SALIDA}")

    for i, chunk in enumerate(chunks):
        print(f"\n=== CHUNK {i} ({len(chunk)} caracteres) ===\n{chunk}")