import time
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "convocatoria_mcdi"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
N_RESULTS = 4

print("Cargando modelo de embeddings...")
embedder = SentenceTransformer(EMBEDDING_MODEL)

print("Conectando a Chroma...")
_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = _client.get_collection(name=COLLECTION_NAME)

print(f"Cargando {LLM_MODEL}...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    torch_dtype=torch.float32,
    device_map="auto",
)
print("Modelo listo.")


def recuperar_contexto(pregunta, n_results=N_RESULTS):
    vector_pregunta = embedder.encode(pregunta).tolist()
    resultados = collection.query(query_embeddings=[vector_pregunta], n_results=n_results)
    return resultados["documents"][0]


def construir_prompt(pregunta, chunks):
    contexto = "\n\n".join(chunks)
    return f"""Eres un asistente que responde dudas sobre la Maestría en Ciencia de Datos
e Información (MCDI) de INFOTEC, usando ÚNICAMENTE la siguiente información oficial.
Si la respuesta no está en el contexto, di que no cuentas con esa información.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""


def generar_respuesta(prompt):
    mensajes = [{"role": "user", "content": prompt}]
    texto_entrada = tokenizer.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)
    entradas = tokenizer([texto_entrada], return_tensors="pt").to(model.device)

    salida = model.generate(**entradas, max_new_tokens=300, temperature=0.3, do_sample=True)
    salida_ids = salida[0][entradas["input_ids"].shape[1]:]
    return tokenizer.decode(salida_ids, skip_special_tokens=True).strip()


def responder_pregunta(pregunta: str) -> dict:
    """Función que llamará la vista de Django."""
    inicio = time.time()
    chunks = recuperar_contexto(pregunta)
    prompt = construir_prompt(pregunta, chunks)
    respuesta = generar_respuesta(prompt)
    duracion = time.time() - inicio

    return {
        "respuesta": respuesta,
        "tiempo": round(duracion, 2),
        "chunks_usados": len(chunks),
    }