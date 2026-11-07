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


def greedy_best_first_search(inicio: Coordenada, destino: Coordenada, obstaculos: Iterable[Coordenada], grid_size: int, costos_movimiento=None):
    obstaculos = set(obstaculos)
    if inicio in obstaculos or destino in obstaculos:
        return None, float("inf"), 0
    cola = []
    heapq.heappush(cola, (distancia_manhattan(inicio, destino), 0, inicio))
    costo = {inicio: 0}
    recorrido = {inicio: None}
    explorados = set()
    descubiertos = {inicio}
    while cola:
        _, _, nodo_actual = heapq.heappop(cola)
        if nodo_actual in explorados:
            continue
        explorados.add(nodo_actual)
        if nodo_actual == destino:
            ruta = []
            actual = nodo_actual
            while actual is not None:
                ruta.append(actual)
                actual = recorrido[actual]
            ruta.reverse()
            return ruta, costo[nodo_actual], len(explorados)
        for desplazamiento in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            fila = nodo_actual[0] + desplazamiento[0]
            columna = nodo_actual[1] + desplazamiento[1]
            vecino = (fila, columna)
            if not (0 <= fila < grid_size and 0 <= columna < grid_size):
                continue
            if vecino in obstaculos:
                continue
            paso = _costo_paso(nodo_actual, vecino, costos_movimiento)
            nuevo_costo = costo[nodo_actual] + paso
            if vecino not in descubiertos:
                descubiertos.add(vecino)
                costo[vecino] = nuevo_costo
                recorrido[vecino] = nodo_actual
                prioridad = distancia_manhattan(vecino, destino)
                heapq.heappush(cola, (prioridad, nuevo_costo, vecino))
    return None, float("inf"), len(explorados)
