from __future__ import annotations

import random
from statistics import mean, stdev
from typing import Sequence


def generar_permuta_aleatoria(entregas, semilla):
    aleatorio = random.Random(semilla)
    return aleatorio.sample(list(entregas), len(entregas))


def evaluar_orden(orden, modelo):
    costo, _ = modelo.evaluar_permuta(orden)
    return costo


def hill_climbing(entregas: Sequence[tuple[int, int]], modelo, soluciones_iniciales: int = 10, iteraciones_maximas: int = 50, semilla: int = 42):
    if soluciones_iniciales < 1 or iteraciones_maximas < 0:
        raise ValueError("[E007] Hill Climbing requiere soluciones iniciales positivas e iteraciones no negativas.")
    mejor_permuta = list(entregas)
    mejor_costo = evaluar_orden(mejor_permuta, modelo)
    evaluaciones = 1
    iteraciones_total = 0
    historial_costos = [mejor_costo]
    costos_finales = []
    for indice in range(soluciones_iniciales):
        actual = generar_permuta_aleatoria(entregas, semilla + indice)
        costo_actual = evaluar_orden(actual, modelo)
        evaluaciones += 1
        for _ in range(iteraciones_maximas):
            iteraciones_total += 1
            mejor_vecino = actual
            mejor_vecino_costo = costo_actual
            for i in range(len(actual)):
                for j in range(i + 1, len(actual)):
                    vecino = actual.copy()
                    vecino[i], vecino[j] = vecino[j], vecino[i]
                    costo_vecino = evaluar_orden(vecino, modelo)
                    evaluaciones += 1
                    if costo_vecino < mejor_vecino_costo:
                        mejor_vecino = vecino
                        mejor_vecino_costo = costo_vecino
            if mejor_vecino_costo >= costo_actual:
                historial_costos.append(mejor_costo)
                break
            actual = mejor_vecino
            costo_actual = mejor_vecino_costo
            if costo_actual < mejor_costo:
                mejor_costo = costo_actual
                mejor_permuta = actual.copy()
            historial_costos.append(mejor_costo)
        costos_finales.append(costo_actual)
        if iteraciones_maximas == 0:
            if costo_actual < mejor_costo:
                mejor_costo = costo_actual
                mejor_permuta = actual.copy()
            historial_costos.append(mejor_costo)
    return {
        "mejor_permuta": mejor_permuta,
        "mejor_costo": mejor_costo,
        "promedio": mean(costos_finales),
        "desviacion_estandar": stdev(costos_finales) if len(costos_finales) > 1 else None,
        "iteraciones": iteraciones_total,
        "evaluaciones": evaluaciones,
        "soluciones_iniciales": soluciones_iniciales,
        "historial_costos": historial_costos,
    }
