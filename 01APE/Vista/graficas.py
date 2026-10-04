# -----------------------------

# Gráfica para las practicas

# -----------------------------

plt.figure(figsize=(10, 5))

plt.plot(t, P, label="Población")

plt.axhline(

    y=K,

    linestyle="--",

    label="Capacidad máxima K"

)

plt.xlabel("Tiempo")

plt.ylabel("Población")

plt.title("Modelo de crecimiento poblacional logístico")

plt.grid(True)

plt.legend()



plt.show()

