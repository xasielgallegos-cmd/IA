from __future__ import annotations

from math import isfinite


def matriz_de_pagos() -> list[list[int]]:
    return [[7, 4, 6], [5, 8, 3], [2, 6, 9]]


def _validar_matriz(matriz):
    if (
        not isinstance(matriz, (list, tuple))
        or not matriz
        or not isinstance(matriz[0], (list, tuple))
        or not matriz[0]
        or any(not isinstance(fila, (list, tuple)) or len(fila) != len(matriz[0]) for fila in matriz)
    ):
        raise ValueError("La matriz de pagos debe ser rectangular y no vacía.")
    if any(
        not isinstance(valor, (int, float))
        or isinstance(valor, bool)
        or not isfinite(valor)
        for fila in matriz
        for valor in fila
    ):
        raise ValueError("Los pagos deben ser numéricos.")


def mejores_respuestas(matriz, *, maximizador_filas=True, maximizador_columnas=True):
    _validar_matriz(matriz)
    respuestas = {"filas": [], "columnas": []}
    for fila in range(len(matriz)):
        mejor = (max if maximizador_filas else min)(matriz[fila])
        respuestas["filas"].append({"fila": fila, "mejor": mejor, "columnas": [j for j, valor in enumerate(matriz[fila]) if valor == mejor]})
    for columna in range(len(matriz[0])):
        pagos = [matriz[fila][columna] for fila in range(len(matriz))]
        mejor = (max if maximizador_columnas else min)(pagos)
        respuestas["columnas"].append({"columna": columna, "mejor": mejor, "filas": [i for i in range(len(matriz)) if matriz[i][columna] == mejor]})
    return respuestas


def estrategias_dominantes(matriz, *, maximizador_filas=True, maximizador_columnas=True):
    _validar_matriz(matriz)
    dominantes = {"filas": [], "columnas": []}
    for fila in range(len(matriz)):
        compara = (lambda a, b: a >= b) if maximizador_filas else (lambda a, b: a <= b)
        if all(compara(matriz[fila][j], matriz[k][j]) for k in range(len(matriz)) for j in range(len(matriz[0])) if k != fila):
            dominantes["filas"].append(fila)
    for columna in range(len(matriz[0])):
        compara = (lambda a, b: a >= b) if maximizador_columnas else (lambda a, b: a <= b)
        if all(compara(matriz[i][columna], matriz[i][j]) for i in range(len(matriz)) for j in range(len(matriz[0])) if j != columna):
            dominantes["columnas"].append(columna)
    return dominantes


def equilibrios_nash(matriz, *, maximizador_filas=True, maximizador_columnas=True):
    respuestas = mejores_respuestas(
        matriz,
        maximizador_filas=maximizador_filas,
        maximizador_columnas=maximizador_columnas,
    )
    equilibrio = []
    for fila in range(len(matriz)):
        for columna in range(len(matriz[0])):
            if columna in respuestas["filas"][fila]["columnas"] and fila in respuestas["columnas"][columna]["filas"]:
                equilibrio.append((fila, columna))
    return equilibrio


def analizar_juego_logistico(matriz=None):
    matriz = matriz_de_pagos() if matriz is None else matriz
    _validar_matriz(matriz)
    mejores = mejores_respuestas(matriz)
    nash = equilibrios_nash(matriz)
    return {
        "matriz": matriz,
        "mejores_respuestas": mejores,
        "domina": estrategias_dominantes(matriz),
        "nash": nash,
        "tipo_pago": "comun_maximizador",
    }
