from __future__ import annotations

from pathlib import Path

from src.busqueda.a_estrella import a_estrella_busqueda
from src.busqueda.greedy import greedy_best_first_search
from src.escenario import Escenario

ROOT = Path(__file__).resolve().parents[1]


def test_ruta_a_estrella():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    ruta, costo, nodos = a_estrella_busqueda(escenario.inicio, escenario.destino, escenario.obstaculos, escenario.grid_size, escenario.costos_movimiento)
    assert ruta is not None
    assert costo > 0
    assert nodos > 0
    assert sum(escenario.costo_movimiento(origen, destino) for origen, destino in zip(ruta, ruta[1:])) == costo


def test_ruta_greedy():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    ruta, costo, nodos = greedy_best_first_search(escenario.inicio, escenario.destino, escenario.obstaculos, escenario.grid_size, escenario.costos_movimiento)
    assert ruta is not None
    assert costo > 0
    assert nodos > 0
    assert sum(escenario.costo_movimiento(origen, destino) for origen, destino in zip(ruta, ruta[1:])) == costo


def test_a_estrella_usa_costos_de_movimiento():
    ruta, costo, _ = a_estrella_busqueda(
        (0, 0),
        (0, 2),
        set(),
        3,
        {(0, 1): 10},
    )
    assert ruta is not None
    assert costo == 4
    assert (0, 1) not in ruta


def test_escenario_sin_solucion():
    escenario = Escenario(grid_size=4, inicio=(0, 0), destino=(3, 3), entregas=[(1, 1), (2, 2), (1, 3)], obstaculos={(1, 0), (0, 1), (2, 1), (1, 2)})
    ruta, costo, nodos = a_estrella_busqueda(escenario.inicio, escenario.destino, escenario.obstaculos, escenario.grid_size, {})
    assert ruta is None
