from __future__ import annotations

from math import isfinite

from src.escenario import Escenario


def validar_escenario(escenario: Escenario) -> None:
    escenario.validar()
    if not escenario.obtener_entregas_ordenadas():
        raise ValueError("El escenario debe incluir entregas.")
    if escenario.inicio in escenario.obstaculos:
        raise ValueError("[E004] El inicio no puede coincidir con un obstáculo.")
    if escenario.destino in escenario.obstaculos:
        raise ValueError("[E004] El destino no puede coincidir con un obstáculo.")


def validar_recurso(escenario: Escenario, recurso: str, valor: int) -> bool:
    if not isinstance(escenario.recursos_disponibles, dict):
        raise ValueError("[E005] Los recursos disponibles deben estar definidos como un objeto.")
    if recurso not in escenario.recursos_disponibles:
        raise ValueError(f"[E005] El recurso requerido '{recurso}' no está definido en el escenario.")
    if not isinstance(valor, (int, float)) or isinstance(valor, bool) or not isfinite(valor) or valor < 0:
        raise ValueError("[E005] El requerimiento de recursos debe ser una cantidad no negativa.")
    disponible = escenario.recursos_disponibles[recurso]
    if not isinstance(disponible, (int, float)) or isinstance(disponible, bool) or not isfinite(disponible):
        raise ValueError(f"[E005] La cantidad disponible para '{recurso}' no es válida.")
    return disponible >= valor


def validar_requerimientos_recursos(escenario: Escenario, requerimientos: dict[str, int]) -> None:
    if not isinstance(requerimientos, dict):
        raise ValueError("[E005] Los requerimientos de recursos deben ser un objeto.")
    for recurso, cantidad in requerimientos.items():
        if not validar_recurso(escenario, recurso, cantidad):
            disponible = escenario.recursos_disponibles[recurso]
            raise ValueError(
                f"[E005] Recursos insuficientes para '{recurso}': "
                f"se requieren {cantidad} y hay {disponible}."
            )


def validar_parametros(parametros: dict) -> None:
    if not isinstance(parametros, dict):
        raise ValueError("[E007] Los parámetros deben estar definidos como un objeto.")
    semilla = parametros.get("semilla", 42)
    if not isinstance(semilla, int) or isinstance(semilla, bool):
        raise ValueError("[E007] 'semilla' debe ser un entero.")
    hill = parametros.get("hill_climbing", {})
    if isinstance(hill, dict):
        hill = {"soluciones_iniciales": 10, "iteraciones_maximas": 50, **hill}
    if not _validar_entero(hill, "soluciones_iniciales", 1) or not _validar_entero(hill, "iteraciones_maximas", 0):
        raise ValueError("[E007] Parámetros inválidos para Hill Climbing.")
    recocido = parametros.get("recocido_simulado", {})
    if isinstance(recocido, dict):
        recocido = {"temperatura_inicial": 120.0, "enfriamiento": 0.95, "iteraciones": 250, **recocido}
    if (
        not isinstance(recocido, dict)
        or not _es_numero_positivo(recocido.get("temperatura_inicial", 120.0))
        or not _es_numero_positivo(recocido.get("enfriamiento", 0.95))
        or recocido.get("enfriamiento", 0.95) >= 1
        or not _validar_entero(recocido, "iteraciones", 0)
    ):
        raise ValueError("[E007] Parámetros inválidos para recocido simulado.")
    genetico = parametros.get("algoritmo_genetico", {})
    if isinstance(genetico, dict):
        genetico = {"tamano_poblacion": 20, "generaciones": 35, "probabilidad_mutacion": 0.15, **genetico}
    mutacion = genetico.get("probabilidad_mutacion", 0.15) if isinstance(genetico, dict) else None
    if (
        not isinstance(genetico, dict)
        or not _validar_entero(genetico, "tamano_poblacion", 1)
        or not _validar_entero(genetico, "generaciones", 0)
        or not isinstance(mutacion, (int, float))
        or isinstance(mutacion, bool)
        or not 0 <= mutacion <= 1
    ):
        raise ValueError("[E007] Parámetros inválidos para el algoritmo genético.")
    busqueda = parametros.get("busqueda", {})
    if not isinstance(busqueda, dict) or busqueda.get("heuristica", "manhattan") != "manhattan":
        raise ValueError("[E007] La búsqueda solo admite la heurística 'manhattan'.")
    minimax = parametros.get("minimax", {})
    if isinstance(minimax, dict):
        minimax = {"profundidad": 3, **minimax}
    if not _validar_entero(minimax, "profundidad", 1):
        raise ValueError("[E007] La profundidad de Minimax debe ser un entero positivo.")
    juego = parametros.get("teoria_juegos", {})
    if not isinstance(juego, dict):
        raise ValueError("[E007] Los parámetros de teoría de juegos deben ser un objeto.")
    matriz = juego.get("matriz_pagos")
    if matriz is not None:
        if (
            not isinstance(matriz, list)
            or not matriz
            or not all(isinstance(fila, list) and fila for fila in matriz)
            or len({len(fila) for fila in matriz}) != 1
            or any(
                not isinstance(valor, (int, float))
                or isinstance(valor, bool)
                or not isfinite(valor)
                for fila in matriz
                for valor in fila
            )
        ):
            raise ValueError("[E007] La matriz de pagos debe ser rectangular, no vacía y numérica.")


def _validar_entero(grupo: dict, nombre: str, minimo: int) -> bool:
    if not isinstance(grupo, dict):
        return False
    valor = grupo.get(nombre)
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo


def _es_numero_positivo(valor) -> bool:
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and isfinite(valor)
        and valor > 0
    )
