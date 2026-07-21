import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("resultados.csv")

plt.figure(figsize=(9, 6))
barras = plt.bar(df["modelo"], df["tiempo_segundos"], color="steelblue")

plt.title("Tiempo de respuesta por modelo LLM ")
plt.ylabel("Tiempo (segundos)")
plt.xlabel("Modelo")
plt.xticks(rotation=20, ha="right")

# Mostrar el valor arriba de cada barra
for barra in barras:
    altura = barra.get_height()
    plt.text(barra.get_x() + barra.get_width()/2, altura + 0.5,
             f"{altura}s", ha="center", va="bottom")

plt.tight_layout()
plt.savefig("grafica_tiempos.png")
plt.show()