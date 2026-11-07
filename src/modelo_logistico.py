from __future__ import annotations

from collections import Counter

from src.escenario import Escenario
from src.busqueda.a_estrella import a_estrella_busqueda


class ModeloLogistico:
    def __init__(self, escenario: Escenario):
        self.escenario = escenario

    def ruta_entre_puntos(self, inicio, destino):
        return a_estrella_busqueda(inicio, destino, self.escenario.obstaculos, self.escenario.grid_size, self.escenario.costos_movimiento)

    def evaluar_permuta(self, permuta):
        if not isinstance(permuta, (list, tuple)):
            raise ValueError("[E008] El orden debe incluir cada entrega exactamente una vez.")
        orden_entregas = []
        for punto in permuta:
            if (
                not isinstance(punto, (list, tuple))
                or len(punto) != 2
                or any(not isinstance(valor, int) or isinstance(valor, bool) for valor in punto)
            ):
                raise ValueError("[E008] El orden contiene una coordenada de entrega inválida.")
            orden_entregas.append(tuple(punto))
        if Counter(orden_entregas) != Counter(self.escenario.entregas):
            raise ValueError("[E008] El orden debe incluir cada entrega exactamente una vez.")
        orden = [self.escenario.inicio] + orden_entregas + [self.escenario.destino]
        costo_total = 0.0
        tramos = []
        for origen, destino in zip(orden, orden[1:]):
            ruta, costo, _ = self.ruta_entre_puntos(origen, destino)
            if ruta is None:
                raise ValueError(f"[E006] No existe ruta entre {origen} y {destino}.")
            costo_total += costo
            tramos.append({"origen": origen, "destino": destino, "ruta": ruta, "costo": costo})
        return costo_total, tramos

    def evaluar_orden_entregas(self, orden):
        costo, tramos = self.evaluar_permuta(orden)
        return {"costo": costo, "tramos": tramos}

    def obtener_costo_total_ruta(self, orden):
        costo, _ = self.evaluar_permuta(orden)
        return costo

    def recurso_suficiente(self, recurso, cantidad):
        return self.escenario.recursos_disponibles.get(recurso, 0) >= cantidad
