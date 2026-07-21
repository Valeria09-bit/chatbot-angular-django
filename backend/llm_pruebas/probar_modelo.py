import time
from transformers import AutoModelForCausalLM, AutoTokenizer

modelo_id = "Qwen/Qwen2.5-3B-Instruct"


print(f"Descargando/cargando {modelo_id}...")
tokenizer = AutoTokenizer.from_pretrained(modelo_id)
modelo = AutoModelForCausalLM.from_pretrained(modelo_id)

mensajes = [{"role": "user", "content": "¿Qué es la Maestría en Ciencia de Datos e Información?"}]
texto = tokenizer.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(texto, return_tensors="pt")

inicio = time.time()
salida = modelo.generate(**inputs, max_new_tokens=100)
duracion = time.time() - inicio

respuesta = tokenizer.decode(salida[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print("\nRespuesta:", respuesta)
print(f"\nTiempo de respuesta: {duracion:.2f} s")