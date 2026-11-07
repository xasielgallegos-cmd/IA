from __future__ import annotations

import heapq
from typing import Iterable

from src.escenario import Coordenada


def distancia_manhattan(origen: Coordenada, destino: Coordenada) -> int:
    return abs(origen[0] - destino[0]) + abs(origen[1] - destino[1])


def _costo_paso(origen: Coordenada, destino: Coordenada, costos_movimiento) -> int:
    if not costos_movimiento:
        return 1
    return costos_movimiento.get((origen, destino), costos_movimiento.get(destino, 1))


def a_estrella_busqueda(inicio: Coordenada, destino: Coordenada, obstaculos: Iterable[Coordenada], grid_size: int, costos_movimiento=None):
    obstaculos = set(obstaculos)
    if inicio in obstaculos or destino in obstaculos:
        return None, float("inf"), 0
    costos_movimiento = costos_movimiento or {}
    costo_minimo = min((1, *costos_movimiento.values()))

    def heuristica(coordenada):
        return distancia_manhattan(coordenada, destino) * costo_minimo

    cola = []
    heapq.heappush(cola, (heuristica(inicio), 0, inicio))
    costo_acumulado = {inicio: 0}
    recorrido = {inicio: None}
    explorados = set()
    while cola:
        prioridad, costo_en_cola, nodo_actual = heapq.heappop(cola)
        if costo_en_cola != costo_acumulado.get(nodo_actual):
            continue
        if nodo_actual in explorados:
            continue
        if nodo_actual == destino:
            ruta = []
            actual = nodo_actual
            while actual is not None:
                ruta.append(actual)
                actual = recorrido[actual]
            ruta.reverse()
            return ruta, costo_acumulado[nodo_actual], len(explorados) + 1
        explorados.add(nodo_actual)
        for desplazamiento in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            fila = nodo_actual[0] + desplazamiento[0]
            columna = nodo_actual[1] + desplazamiento[1]
            vecino = (fila, columna)
            if not (0 <= fila < grid_size and 0 <= columna < grid_size):
                continue
            if vecino in obstaculos:
                continue
            paso = _costo_paso(nodo_actual, vecino, costos_movimiento)
            nuevo_costo = costo_acumulado[nodo_actual] + paso
            if vecino not in costo_acumulado or nuevo_costo < costo_acumulado[vecino]:
                costo_acumulado[vecino] = nuevo_costo
                recorrido[vecino] = nodo_actual
                heapq.heappush(cola, (nuevo_costo + heuristica(vecino), nuevo_costo, vecino))
    return None, float("inf"), len(explorados)
