from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def mensaje_view(request):
    data = {
        "mensaje": "Mensaje desde Django",
        "mensaje2": "Angular recibiendo segundo msj",
    }
    return JsonResponse(data)


@csrf_exempt
def sumar_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        a = body.get('a')
        b = body.get('b')
        resultado = a + b
        return JsonResponse({'resultado': resultado})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def concatenar_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        texto1 = body.get('texto1', '')
        texto2 = body.get('texto2', '')
        resultado = texto1 + texto2
        return JsonResponse({'resultado': resultado})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def invertir_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        arreglo = body.get('arreglo', [])
        resultado = arreglo[::-1]
        return JsonResponse({'resultado': resultado})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ============================================================
#  RAG: recuperación con ChromaDB + generación con Qwen2.5-1.5B
# ============================================================

# --- Modelo de embeddings (para buscar en Chroma) ---
_modelo_embeddings = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# Ruta donde quedó guardada la carpeta chroma_db
# (chroma_db está en ~/chatbot, y este views.py está en ~/chatbot/backend/backend/)
RUTA_CHROMA_DB = "/home/vale/chatbot/chroma_db"

# --- Modelo LLM (para generar la respuesta) ---
_LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

_tokenizer = AutoTokenizer.from_pretrained(_LLM_MODEL)
_modelo_llm = AutoModelForCausalLM.from_pretrained(
    _LLM_MODEL,
    torch_dtype=torch.float32,  # usa torch.float16 si tienes GPU compatible
    device_map="auto",
)


def buscar_contexto(pregunta, n_resultados=3):
    """Busca los chunks más relevantes en ChromaDB para una pregunta dada."""
    client = chromadb.PersistentClient(path=RUTA_CHROMA_DB)
    coleccion = client.get_collection("convocatoria_mcdi")

    embedding_pregunta = _modelo_embeddings.encode([pregunta]).tolist()

    resultados = coleccion.query(
        query_embeddings=embedding_pregunta,
        n_results=n_resultados,
    )

    return resultados["documents"][0]


def construir_prompt(pregunta, chunks):
    """Arma el prompt final que se le pasará al LLM, con el contexto recuperado."""
    contexto = "\n\n".join(chunks)
    return f"""Eres un asistente que responde dudas sobre la Maestría en Ciencia de Datos
e Información (MCDI) de INFOTEC, usando ÚNICAMENTE la siguiente información oficial.
Si la respuesta no está en el contexto, di que no cuentas con esa información.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""


def generar_respuesta_llm(prompt):
    """Genera la respuesta del LLM a partir del prompt con contexto."""
    mensajes = [{"role": "user", "content": prompt}]
    texto_entrada = _tokenizer.apply_chat_template(
        mensajes, tokenize=False, add_generation_prompt=True
    )
    entradas = _tokenizer([texto_entrada], return_tensors="pt").to(_modelo_llm.device)

    salida = _modelo_llm.generate(
        **entradas, max_new_tokens=300, temperature=0.3, do_sample=True
    )
    salida_ids = salida[0][entradas["input_ids"].shape[1]:]
    return _tokenizer.decode(salida_ids, skip_special_tokens=True).strip()


@csrf_exempt
def preguntar_view(request):
    """
    Vista que recibe la pregunta del usuario desde Angular,
    busca el contexto relevante en Chroma, genera la respuesta con el LLM
    y la regresa a Angular.
    """
    if request.method == 'POST':
        body = json.loads(request.body)
        pregunta = body.get('pregunta', '')

        if not pregunta:
            return JsonResponse({'error': 'No se recibió ninguna pregunta'}, status=400)

        chunks = buscar_contexto(pregunta, n_resultados=5)
        prompt = construir_prompt(pregunta, chunks)
        respuesta = generar_respuesta_llm(prompt)

        return JsonResponse({
            'pregunta': pregunta,
            'respuesta': respuesta,
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)