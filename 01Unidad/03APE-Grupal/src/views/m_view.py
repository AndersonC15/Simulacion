"""Vista: animación interactiva, tablas y gráficas de la simulación M/M/1."""

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from src.models.m_model import ComparacionEscenario


def _imprimir_tabla_comparacion(resultados: list[ComparacionEscenario]) -> None:
    header = (
        f"{'Esc.':<6}{'Métrica':<12}{'Teórico':>12}{'Simulado':>12}"
        f"{'Error %':>12}"
    )
    print("\n" + "=" * len(header))
    print("COMPARACIÓN DE RESULTADOS TEÓRICOS VS SIMULADOS")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    metricas = [
        ("ρ", lambda r: r.teoricos.rho, lambda r: r.simulados.utilizacion),
        ("L", lambda r: r.teoricos.L, lambda r: r.simulados.L),
        ("Lq", lambda r: r.teoricos.Lq, lambda r: r.simulados.Lq),
        ("W", lambda r: r.teoricos.W, lambda r: r.simulados.W),
        ("Wq", lambda r: r.teoricos.Wq, lambda r: r.simulados.Wq),
    ]

    for i, res in enumerate(resultados, start=1):
        cond = res.escenario.condicion
        print(f"\nEscenario {i} (λ={res.escenario.lam}, "
              f"μ={res.escenario.mu}) — {cond}")
        for nombre, f_teo, f_sim in metricas:
            teo = f_teo(res)
            sim = f_sim(res)
            error = abs(sim - teo) / teo * 100 if teo != 0 else 0.0
            print(f"{'':<6}{nombre:<12}{teo:>12.4f}{sim:>12.4f}{error:>11.2f}%")

    print("\n" + "=" * len(header))


def _imprimir_resumen_escenarios(resultados: list[ComparacionEscenario]) -> None:
    print("\nRESUMEN DE ESCENARIOS")
    print("-" * 60)
    for i, res in enumerate(resultados, start=1):
        e = res.escenario
        print(
            f"Escenario {i}: λ={e.lam}, μ={e.mu}, ρ={res.teoricos.rho:.4f} "
            f"({e.condicion})"
        )
        print(
            f"  Teóricos : L={res.teoricos.L:.4f}, Lq={res.teoricos.Lq:.4f}, "
            f"W={res.teoricos.W:.4f}, Wq={res.teoricos.Wq:.4f}"
        )
        print(
            f"  Simulados: L={res.simulados.L:.4f}, Lq={res.simulados.Lq:.4f}, "
            f"W={res.simulados.W:.4f}, Wq={res.simulados.Wq:.4f}"
        )
    print()


def animar_simulacion(resultados: list[ComparacionEscenario]) -> None:
    """Animación interativa de las llegadas, cola y atención del servidor."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Simulación M/M/1 — Animación de Llegadas y Atención",
        fontsize=13,
        fontweight="bold",
    )

    animadores = []
    for i, (res, ax) in enumerate(zip(resultados, axes)):
        lam = res.escenario.lam
        mu = res.escenario.mu
        llegadas = np.array(res.reloj_llegadas)
        cola = np.array(res.tamanios_cola)
        espera = np.array(res.tiempos_espera)

        num_frames = min(400, len(llegadas))
        indices = np.linspace(0, len(llegadas) - 1, num_frames, dtype=int)

        ax.set_xlim(llegadas.min(), llegadas[indices[-1]])
        ax.set_ylim(-0.5, max(cola.max(), 5) + 1)
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Clientes en cola")
        ax.set_title(f"Escenario {i + 1}: λ={lam}, μ={mu}")
        ax.grid(True, alpha=0.3)

        linea, = ax.plot([], [], "b-", linewidth=1.2, label="Tamaño cola")
        punto, = ax.plot([], [], "ro", markersize=8, label="Llegada actual")
        texto = ax.text(
            0.02, 0.95, "", transform=ax.transAxes,
            fontsize=9, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )
        ax.legend(loc="upper right", fontsize=8)

        def init(linea=linea, punto=punto, texto=texto):
            linea.set_data([], [])
            punto.set_data([], [])
            texto.set_text("")
            return linea, punto, texto

        def update(
            frame,
            linea=linea,
            punto=punto,
            texto=texto,
            indices=indices,
            llegadas=llegadas,
            cola=cola,
            espera=espera,
            lam=lam,
            mu=mu,
            ax=ax,
        ):
            idx = indices[frame]
            t = llegadas[idx]
            c = cola[idx]
            w = espera[idx] if idx < len(espera) else 0.0

            linea.set_data(llegadas[: idx + 1], cola[: idx + 1])
            punto.set_data([t], [c])
            texto.set_text(f"t={t:.1f}\nCola={c}\nEspera={w:.3f}")

            if frame > 0:
                prev = indices[frame - 1]
                ax.set_xlim(
                    max(llegadas.min(), llegadas[prev] - 20),
                    llegadas[prev] + 20,
                )
            return linea, punto, texto

        anim = animation.FuncAnimation(
            fig,
            update,
            init_func=init,
            frames=num_frames,
            interval=50,
            blit=True,
            repeat=False,
        )
        animadores.append(anim)

    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.show()


def generar_graficas(resultados: list[ComparacionEscenario]) -> None:
    """Genera gráficas de cola y tiempos de espera para los 3 escenarios."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "Simulación M/M/1 — Cola y Tiempos de Espera por Escenario",
        fontsize=14,
        fontweight="bold",
    )

    etiquetas = [
        f"Esc {i}\nλ={r.escenario.lam}, μ={r.escenario.mu}"
        for i, r in enumerate(resultados, start=1)
    ]

    for i, res in enumerate(resultados):
        ax_cola = axes[0, i]
        ax_cola.plot(res.reloj_llegadas[:800], res.tamanios_cola[:800],
                     color="tab:blue", linewidth=0.8)
        ax_cola.set_title(f"Tamaño de la cola\n{etiquetas[i]}")
        ax_cola.set_xlabel("Tiempo")
        ax_cola.set_ylabel("Clientes en cola")
        ax_cola.grid(True, alpha=0.3)

        ax_esp = axes[1, i]
        ax_esp.hist(res.tiempos_espera, bins=40, color="tab:orange",
                    edgecolor="black", alpha=0.75, density=True)
        media = res.simulados.Wq
        ax_esp.axvline(media, color="red", linestyle="--",
                       label=f"Media simulada = {media:.4f}")
        ax_esp.axvline(res.teoricos.Wq, color="green", linestyle=":",
                       label=f"Media teórica = {res.teoricos.Wq:.4f}")
        ax_esp.set_title(f"Distribución tiempo de espera en cola\n{etiquetas[i]}")
        ax_esp.set_xlabel("Tiempo de espera")
        ax_esp.set_ylabel("Densidad")
        ax_esp.legend(fontsize=8)
        ax_esp.grid(True, alpha=0.3)

    plt.tight_layout(rect=(0, 0, 1, 0.95))
    plt.savefig("graficas_mm1.png", dpi=150)
    plt.show()


def mostrar_resultados(resultados: list[ComparacionEscenario],
                       con_animacion: bool = True) -> None:
    _imprimir_resumen_escenarios(resultados)
    _imprimir_tabla_comparacion(resultados)
    if con_animacion:
        animar_simulacion(resultados)
    generar_graficas(resultados)
