from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from math import isfinite
from pathlib import Path

Coordenada = tuple[int, int]


@dataclass
class Escenario:
    grid_size: int = 12
    inicio: Coordenada = (0, 0)
    destino: Coordenada = (11, 11)
    entregas: list[Coordenada] = field(default_factory=list)
    obstaculos: set[Coordenada] = field(default_factory=set)
    recursos_disponibles: dict[str, int] = field(default_factory=lambda: {"transporte": 10, "combustible": 12})
    restricciones: dict[str, int] = field(default_factory=lambda: {"capacidad": 8})
    competidor: dict = field(default_factory=lambda: {"modificacion_recursos": {"combustible": -2}, "costo_adicional": 1})
    costos_movimiento: dict[tuple[int, int], int] = field(default_factory=dict)

    @classmethod
    def desde_json(cls, path: str | Path) -> "Escenario":
        ruta = Path(path)
        if not ruta.is_file():
            raise ValueError(f"[E001] No se encontró el archivo de escenario: {ruta}")
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except JSONDecodeError as error:
            raise ValueError(f"[E002] El JSON del escenario no es válido: {error}") from error
        if not isinstance(datos, dict):
            raise ValueError("[E002] El contenido del escenario debe ser un objeto JSON.")
        escenario = cls(
            grid_size=datos.get("grid_size", 12),
            inicio=_leer_coordenada(datos.get("inicio", (0, 0)), "inicio"),
            destino=_leer_coordenada(datos.get("destino", (11, 11)), "destino"),
            entregas=[_leer_coordenada(punto, "entrega") for punto in datos.get("entregas", [])],
            obstaculos={_leer_coordenada(punto, "obstáculo") for punto in datos.get("obstaculos", [])},
            recursos_disponibles=datos.get("recursos_disponibles", {"transporte": 10, "combustible": 12}),
            restricciones=datos.get("restricciones", {"capacidad": 8}),
            competidor=datos.get("competidor", {"modificacion_recursos": {"combustible": -2}, "costo_adicional": 1}),
        )
        escenario.costos_movimiento = {}
        return escenario

    def validar(self) -> None:
        errores: list[str] = []
        if not isinstance(self.grid_size, int) or isinstance(self.grid_size, bool) or self.grid_size <= 0:
            errores.append("[E003] La cuadrícula debe tener tamaño entero positivo.")
            if errores:
                raise ValueError("; ".join(errores))
        if not self._coordenada_valida(self.inicio):
            errores.append("[E003] El punto de inicio está fuera de la cuadrícula o no es válido.")
        if not self._coordenada_valida(self.destino):
            errores.append("[E003] El punto de destino está fuera de la cuadrícula o no es válido.")
        if self.inicio == self.destino:
            errores.append("[E003] El inicio y el destino no pueden coincidir.")
        if self.inicio in self.obstaculos or self.destino in self.obstaculos:
            errores.append("[E004] El inicio y el destino no pueden estar sobre un obstáculo.")
        if len(self.entregas) < 3:
            errores.append("Debe existir al menos tres entregas.")
        for punto in self.entregas:
            if not self._coordenada_valida(punto):
                errores.append(f"[E003] La entrega {punto} está fuera de la cuadrícula o no es válida.")
            if punto in self.obstaculos:
                errores.append(f"[E004] La entrega {punto} no puede estar sobre un obstáculo.")
        if len(set(self.entregas)) != len(self.entregas):
            errores.append("[E003] Las entregas no pueden duplicarse.")
        if not isinstance(self.recursos_disponibles, dict) or any(
            not isinstance(valor, (int, float))
            or isinstance(valor, bool)
            or not isfinite(valor)
            or valor < 0
            for valor in self.recursos_disponibles.values()
        ):
            errores.append("[E005] Los recursos disponibles deben ser cantidades numéricas no negativas.")
        if not isinstance(self.restricciones, dict) or any(
            not isinstance(valor, (int, float))
            or isinstance(valor, bool)
            or not isfinite(valor)
            or valor <= 0
            for valor in self.restricciones.values()
        ):
            errores.append("[E007] Las restricciones deben ser cantidades numéricas positivas.")
        if errores:
            raise ValueError("; ".join(errores))

    def _coordenada_valida(self, coordenada: Coordenada) -> bool:
        if (
            not isinstance(coordenada, tuple)
            or len(coordenada) != 2
            or any(not isinstance(valor, int) or isinstance(valor, bool) for valor in coordenada)
        ):
            return False
        fila, columna = coordenada
        return 0 <= fila < self.grid_size and 0 <= columna < self.grid_size

    def cargar_costos_desde_csv(self, path: str | Path) -> None:
        ruta = Path(path)
        costos: dict[Coordenada, int] = {}
        try:
            with ruta.open("r", encoding="utf-8", newline="") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    posicion = (int(fila["fila"]), int(fila["columna"]))
                    costo = int(fila["costo"])
                    if not self._coordenada_valida(posicion) or costo < 1:
                        raise ValueError(f"[E007] Costo o coordenada inválidos en {ruta}: {fila}")
                    costos[posicion] = costo
        except (KeyError, TypeError, csv.Error, ValueError) as error:
            if str(error).startswith("[E007]"):
                raise
            raise ValueError(f"[E007] Archivo de costos inválido {ruta}: {error}") from error
        self.costos_movimiento = costos

    def costo_movimiento(self, origen: Coordenada, destino: Coordenada) -> int:
        clave = (origen, destino)
        if clave in self.costos_movimiento:
            return self.costos_movimiento[clave]
        if destino in self.costos_movimiento:
            return self.costos_movimiento[destino]
        return 1

    def obtener_obstaculos(self) -> set[Coordenada]:
        return set(self.obstaculos)

    def obtener_entregas_ordenadas(self) -> list[Coordenada]:
        return list(self.entregas)

    def to_dict(self) -> dict:
        return {
            "grid_size": self.grid_size,
            "inicio": list(self.inicio),
            "destino": list(self.destino),
            "entregas": [list(entrega) for entrega in self.entregas],
            "obstaculos": [list(obstaculo) for obstaculo in sorted(self.obstaculos)],
            "recursos_disponibles": self.recursos_disponibles,
            "restricciones": self.restricciones,
            "competidor": self.competidor,
        }


def construir_escenario_por_defecto() -> Escenario:
    escenario = Escenario(
        grid_size=12,
        inicio=(0, 0),
        destino=(11, 11),
        entregas=[(2, 9), (5, 2), (8, 8), (9, 3)],
        obstaculos={(3, 3), (3, 4), (3, 5), (6, 5), (6, 6), (6, 7), (9, 9), (8, 9), (2, 6)},
    )
    escenario.validar()
    return escenario


def _leer_coordenada(valor, etiqueta: str) -> Coordenada:
    if (
        not isinstance(valor, (list, tuple))
        or len(valor) != 2
        or any(not isinstance(item, int) or isinstance(item, bool) for item in valor)
    ):
        raise ValueError(f"[E003] La coordenada de {etiqueta} debe contener dos enteros.")
    return valor[0], valor[1]
