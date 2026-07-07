from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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