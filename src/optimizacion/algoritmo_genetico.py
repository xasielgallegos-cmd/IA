from __future__ import annotations

import random
import time
import math
from statistics import mean, stdev
from typing import Sequence


def costo_orden(orden, modelo):
    costo, _ = modelo.evaluar_permuta(orden)
    return costo


def inicializar_poblacion(entregas, tamano, aleatorio):
    poblacion = []
    for _ in range(tamano):
        poblacion.append(aleatorio.sample(list(entregas), len(entregas)))
    return poblacion


def seleccionar_padre(poblacion, puntajes, aleatorio):
    total = sum(puntajes)
    valor = aleatorio.random() * total
    acumulado = 0.0
    for individuo, puntaje in zip(poblacion, puntajes):
        acumulado += puntaje
        if acumulado >= valor:
            return individuo
    return poblacion[0]


def cruzar_orden(padre1, padre2, aleatorio):
    hijo = [None] * len(padre1)
    inicio = aleatorio.randrange(len(padre1))
    fin = aleatorio.randrange(len(padre1))
    inicio, fin = sorted((inicio, fin))
    for indice in range(inicio, fin + 1):
        hijo[indice] = padre1[indice]
    indice = 0
    for valor in padre2:
        if valor not in hijo:
            while hijo[indice] is not None:
                indice += 1
            hijo[indice] = valor
    return hijo


def mutar_orden(orden, aleatorio, probabilidad=0.15):
    if aleatorio.random() > probabilidad:
        return orden
    nueva = orden.copy()
    i, j = aleatorio.sample(range(len(nueva)), 2)
    nueva[i], nueva[j] = nueva[j], nueva[i]
    return nueva


def ejecutar_algoritmo_genetico(modelo, entregas, tamano_poblacion=20, generaciones=35, probabilidad_mutacion=0.15, semilla=42):
    if (
        not entregas
        or not isinstance(tamano_poblacion, int)
        or isinstance(tamano_poblacion, bool)
        or tamano_poblacion < 1
        or not isinstance(generaciones, int)
        or isinstance(generaciones, bool)
        or generaciones < 0
        or not isinstance(probabilidad_mutacion, (int, float))
        or isinstance(probabilidad_mutacion, bool)
        or not math.isfinite(probabilidad_mutacion)
        or not 0 <= probabilidad_mutacion <= 1
    ):
        raise ValueError("[E007] Parámetros inválidos para el algoritmo genético.")
    aleatorio = random.Random(semilla)
    poblacion = inicializar_poblacion(entregas, tamano_poblacion, aleatorio)
    tiempo_inicio = time.perf_counter()
    costos = [costo_orden(individuo, modelo) for individuo in poblacion]
    evaluaciones = len(poblacion)
    indice_mejor = min(range(len(poblacion)), key=costos.__getitem__)
    mejor = poblacion[indice_mejor].copy()
    mejor_costo = costos[indice_mejor]
    historial_costos = [mejor_costo]
    for _ in range(generaciones):
        puntajes = [1.0 / (1.0 + max(costo, 1e-9)) for costo in costos]
        nueva_poblacion = []
        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = seleccionar_padre(poblacion, puntajes, aleatorio)
            padre2 = seleccionar_padre(poblacion, puntajes, aleatorio)
            hijo = cruzar_orden(padre1, padre2, aleatorio)
            hijo = mutar_orden(hijo, aleatorio, probabilidad_mutacion)
            nueva_poblacion.append(hijo)
        poblacion = nueva_poblacion
        costos = [costo_orden(individuo, modelo) for individuo in poblacion]
        evaluaciones += len(poblacion)
        indice_mejor = min(range(len(poblacion)), key=costos.__getitem__)
        if costos[indice_mejor] < mejor_costo:
            mejor = poblacion[indice_mejor].copy()
            mejor_costo = costos[indice_mejor]
        historial_costos.append(mejor_costo)
    tiempo_total = time.perf_counter() - tiempo_inicio
    return {
        "mejor_permuta": mejor,
        "mejor_costo": mejor_costo,
        "promedio": mean(costos),
        "desviacion_estandar": stdev(costos) if len(costos) > 1 else None,
        "evaluaciones": evaluaciones,
        "tiempo_segundos": tiempo_total,
        "historial_costos": historial_costos,
    }
