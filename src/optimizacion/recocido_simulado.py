from __future__ import annotations

import math
import random
from statistics import mean, stdev
import time


def costo_orden(orden, modelo):
    costo, _ = modelo.evaluar_permuta(orden)
    return costo


def vecino_aleatorio(orden, aleatorio):
    nueva = orden.copy()
    i, j = aleatorio.sample(range(len(nueva)), 2)
    nueva[i], nueva[j] = nueva[j], nueva[i]
    return nueva


def recocido_simulado(modelo, entregas, temperatura_inicial=120.0, enfriamiento=0.95, iteraciones=250, semilla=42):
    if (
        not entregas
        or not isinstance(temperatura_inicial, (int, float))
        or isinstance(temperatura_inicial, bool)
        or not math.isfinite(temperatura_inicial)
        or temperatura_inicial <= 0
        or not isinstance(enfriamiento, (int, float))
        or isinstance(enfriamiento, bool)
        or not math.isfinite(enfriamiento)
        or not 0 < enfriamiento < 1
        or not isinstance(iteraciones, int)
        or isinstance(iteraciones, bool)
        or iteraciones < 0
    ):
        raise ValueError("[E007] Parámetros inválidos para recocido simulado.")
    aleatorio = random.Random(semilla)
    actual = aleatorio.sample(list(entregas), len(entregas))
    costo_actual = costo_orden(actual, modelo)
    mejor = actual.copy()
    mejor_costo = costo_actual
    temperatura = temperatura_inicial
    tiempo_inicio = time.perf_counter()
    evaluaciones = 0
    historial_costos = [mejor_costo]
    costos_evaluados = []
    for _ in range(iteraciones):
        candidato = vecino_aleatorio(actual, aleatorio)
        costo_candidato = costo_orden(candidato, modelo)
        evaluaciones += 1
        costos_evaluados.append(costo_candidato)
        diferencia = costo_candidato - costo_actual
        if diferencia < 0 or aleatorio.random() < math.exp(-diferencia / temperatura):
            actual = candidato
            costo_actual = costo_candidato
        if costo_actual < mejor_costo:
            mejor = actual.copy()
            mejor_costo = costo_actual
        historial_costos.append(mejor_costo)
        temperatura *= enfriamiento
    tiempo_total = time.perf_counter() - tiempo_inicio
    return {
        "mejor_permuta": mejor,
        "mejor_costo": mejor_costo,
        "promedio": mean(costos_evaluados) if costos_evaluados else mejor_costo,
        "desviacion_estandar": stdev(costos_evaluados) if len(costos_evaluados) > 1 else None,
        "evaluaciones": evaluaciones,
        "tiempo_segundos": tiempo_total,
        "historial_costos": historial_costos,
    }
