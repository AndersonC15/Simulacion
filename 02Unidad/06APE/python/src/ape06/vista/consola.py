"""Vista de consola: comunica resultados sin decidir las hipotesis."""

import statistics

from ape06.modelo.datos import Analisis, Medicion


class VistaConsola:
    def mostrar_analisis(self, analisis: Analisis) -> None:
        m = analisis.muestra
        p = m.parametros
        print(f"\n{p.nombre.upper()} | N={len(m.valores)} | X0={p.semilla}, a={p.a}, c={p.c}, m={p.m}")
        print("Primeros 10 valores (la secuencia completa se guarda en CSV):")
        for i, (x, u) in enumerate(zip(m.estados[:10], m.valores[:10]), 1):
            print(f"  {i:2d}: X={x:12d}, U={u:.12f}")
        print(f"Media={analisis.media:.8f}, varianza poblacional={analisis.varianza:.8f}")
        periodo = analisis.periodo_observado
        print(f"Periodo observado: {periodo if periodo is not None else 'no detectado en la muestra; no se afirma el periodo total'}")
        for prueba in analisis.pruebas:
            if prueba.estadistico is None:
                print(f"{prueba.nombre}: {prueba.decision}. {prueba.nota}")
                continue
            print(f"{prueba.nombre}: T={prueba.estadistico:.10g}, p={prueba.valor_p:.10g}, "
                  f"critico={prueba.critico:.10g}, alfa={prueba.alfa}: {prueba.decision}")
            if prueba.detalles:
                print("  " + ", ".join(f"{k}={v:.10g}" for k, v in prueba.detalles.items()))
            for intervalo in prueba.intervalos:
                print(f"  [{intervalo.inferior:.1f}, {intervalo.superior:.1f}): "
                      f"O={intervalo.observada}, E={intervalo.esperada:.2f}, aporte={intervalo.aporte:.6f}")
        print("No rechazar H0 no demuestra aleatoriedad ni independencia completa.")

    def mostrar_medicion(self, medicion: Medicion) -> None:
        r = medicion.resultado
        print(f"{medicion.parametros.nombre:8} N={r.puntos:7d} puntos | pi={r.estimacion:.8f} | "
              f"error={r.error_absoluto:.8f} | mediana={statistics.median(medicion.segundos):.6f} s")
