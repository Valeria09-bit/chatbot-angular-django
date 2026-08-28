"""
RAG completo: Chroma (embeddings persistidos) + Qwen2.5-1.5B-Instruct
----------------------------------------------------------------------
Este script:
1. Se conecta a la base de Chroma.
2. Recupera los chunks más relevantes para la pregunta del usuario.
3. Arma un prompt con ese contexto.
4. Se lo pasa al modelo escogido del cual es: Qwen2.5-1.5B-Instruct para generar la respuesta.


"""

# ============ CONFIGURACIÓN ============
CHROMA_PATH = "./chroma_db"                 # carpeta donde persististe Chroma
COLLECTION_NAME = "convocatoria_mcdi"     # nombre de tu colección en Chroma
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2" # el mismo que usaste al indexar
LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"    #modelo elegido para generar respuestas
N_RESULTS = 4                             # cuántos chunks recuperar por pregunta
# =======================================================

import time
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def cargar_chroma():
    """Conecta a la base de Chroma."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    return collection


def recuperar_contexto(pregunta, collection, embedder, n_results=N_RESULTS):
    """Convierte la pregunta en vector y busca los chunks más parecidos en Chroma."""
    vector_pregunta = embedder.encode(pregunta).tolist()
    resultados = collection.query(
        query_embeddings=[vector_pregunta],
        n_results=n_results,
    )
    chunks_recuperados = resultados["documents"][0]
    return chunks_recuperados


def construir_prompt(pregunta, chunks):
    """Arma el prompt final que se le pasará al LLM, con el contexto recuperado."""
    contexto = "\n\n".join(chunks)
    prompt = f"""Eres un asistente que responde dudas sobre la Maestría en Ciencia de Datos
e Información (MCDI) de INFOTEC, usando ÚNICAMENTE la siguiente información oficial.
Si la respuesta no está en el contexto, di que no cuentas con esa información.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""
    return prompt


def generar_respuesta(prompt, model, tokenizer):
    """Genera la respuesta del LLM a partir del prompt con contexto."""
    mensajes = [{"role": "user", "content": prompt}]
    texto_entrada = tokenizer.apply_chat_template(
        mensajes, tokenize=False, add_generation_prompt=True
    )
    entradas = tokenizer([texto_entrada], return_tensors="pt").to(model.device)

    salida = model.generate(
        **entradas,
        max_new_tokens=300,
        temperature=0.3,
        do_sample=True,
    )
    salida_ids = salida[0][entradas["input_ids"].shape[1]:]
    respuesta = tokenizer.decode(salida_ids, skip_special_tokens=True)
    return respuesta


def main():
    print("Cargando modelo de embeddings...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    print("Conectando a Chroma...")
    collection = cargar_chroma()

    print(f"Cargando {LLM_MODEL} (puede tardar un poco la primera vez)...")
    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL,
        torch_dtype=torch.float32,  # usa torch.float16 si tienes GPU compatible
        device_map="auto",
    )

    print("\n=== Listo. Escribe tu pregunta (o 'salir' para terminar) ===\n")

    while True:
        pregunta = input("Pregunta: ").strip()
        if pregunta.lower() in ("salir", "exit", "quit"):
            break
        if not pregunta:
            continue

        inicio = time.time()

        chunks = recuperar_contexto(pregunta, collection, embedder)
        prompt = construir_prompt(pregunta, chunks)
        respuesta = generar_respuesta(prompt, model, tokenizer)

        duracion = time.time() - inicio

        print("\n--- Chunks recuperados ---")
        for i, c in enumerate(chunks, 1):
            print(f"[{i}] {c[:150]}...")

        print(f"\n--- Respuesta ({duracion:.2f}s) ---")
        print(respuesta)
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()