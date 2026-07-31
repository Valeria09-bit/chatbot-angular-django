from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import chromadb
from sentence_transformers import SentenceTransformer


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
# NUEVO: Vista de recuperación con ChromaDB (RAG)
# ============================================================

# Cargamos el modelo UNA sola vez cuando arranca el servidor,
# no en cada request (si no, cada pregunta tardaría mucho).
_modelo_embeddings = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# Ruta donde quedó guardada la carpeta chroma_db
# (chroma_db está en ~/chatbot, y este views.py está en ~/chatbot/backend/backend/)
RUTA_CHROMA_DB = "/home/vale/chatbot/chroma_db"


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


@csrf_exempt
def preguntar_view(request):
    """
    Vista que recibe la pregunta del usuario desde Angular,
    busca el contexto relevante en Chroma y lo regresa.
    """
    if request.method == 'POST':
        body = json.loads(request.body)
        pregunta = body.get('pregunta', '')

        if not pregunta:
            return JsonResponse({'error': 'No se recibió ninguna pregunta'}, status=400)

        contexto = buscar_contexto(pregunta, n_resultados=5)

        return JsonResponse({
            'pregunta': pregunta,
            'contexto_encontrado': contexto,
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)