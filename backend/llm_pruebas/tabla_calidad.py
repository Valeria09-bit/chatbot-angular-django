import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("resultados.csv")

fig, ax = plt.subplots(figsize=(10, 3))
ax.axis("off")

tabla = ax.table(
    cellText=df[["modelo", "parametros", "tiempo_segundos", "calidad_respuesta"]].values,
    colLabels=["Modelo", "Parámetros", "Tiempo (s)", "Calidad de respuesta"],
    cellLoc="left",
    loc="center"
)

tabla.auto_set_font_size(False)
tabla.set_fontsize(9)
tabla.scale(1, 2.2)
tabla.auto_set_column_width(col=list(range(4)))

plt.tight_layout()
plt.savefig("tabla_calidad.png", dpi=150, bbox_inches="tight")
plt.show()