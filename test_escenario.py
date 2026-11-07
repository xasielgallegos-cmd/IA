from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.escenario import Escenario
from src.validaciones import validar_escenario, validar_parametros, validar_requerimientos_recursos
from src.modelo_logistico import ModeloLogistico
from src.busqueda.a_estrella import a_estrella_busqueda


ROOT = Path(__file__).resolve().parents[1]


def test_carga_escenario():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    assert escenario.grid_size == 12
    assert len(escenario.entregas) >= 3


def test_validacion_escenario():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    validar_escenario(escenario)
    assert escenario.inicio == (0, 0)


def test_detecta_obstaculos():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    assert (3, 3) in escenario.obstaculos


def test_escenario_invalido():
    escenario = Escenario(grid_size=12, inicio=(0, 0), destino=(11, 11), entregas=[(1, 1)])
    with pytest.raises(ValueError):
        escenario.validar()


def test_e001_archivo_escenario_faltante(tmp_path):
    with pytest.raises(ValueError, match=r"\[E001\]"):
        Escenario.desde_json(tmp_path / "faltante.json")


def test_e002_json_mal_formado(tmp_path):
    archivo = tmp_path / "escenario.json"
    archivo.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match=r"\[E002\]"):
        Escenario.desde_json(archivo)


def test_e003_coordenada_fuera_de_limites():
    escenario = Escenario(grid_size=4, inicio=(-1, 0), destino=(3, 3), entregas=[(0, 1), (1, 1), (2, 2)])
    with pytest.raises(ValueError, match=r"\[E003\]"):
        escenario.validar()


def test_e004_entrega_sobre_obstaculo():
    escenario = Escenario(
        grid_size=4,
        inicio=(0, 0),
        destino=(3, 3),
        entregas=[(1, 1), (1, 2), (2, 2)],
        obstaculos={(1, 1)},
    )
    with pytest.raises(ValueError, match=r"\[E004\]"):
        escenario.validar()


def test_e005_recursos_insuficientes():
    escenario = Escenario(
        grid_size=4,
        inicio=(0, 0),
        destino=(3, 3),
        entregas=[(0, 1), (1, 1), (2, 2)],
        recursos_disponibles={"combustible": 2},
    )
    with pytest.raises(ValueError, match=r"\[E005\]"):
        validar_requerimientos_recursos(escenario, {"combustible": 3})


def test_e006_sin_ruta():
    escenario = Escenario(grid_size=4, inicio=(0, 0), destino=(3, 3), entregas=[(1, 1), (2, 2), (1, 3)], obstaculos={(1, 0), (0, 1)})
    ruta, costo, _ = a_estrella_busqueda(
        escenario.inicio,
        escenario.destino,
        escenario.obstaculos,
        escenario.grid_size,
        {},
    )
    assert ruta is None
    assert costo == float("inf")
    with pytest.raises(ValueError, match=r"\[E006\]"):
        ModeloLogistico(escenario).evaluar_permuta(escenario.entregas)


def test_e007_parametros_invalidos():
    with pytest.raises(ValueError, match=r"\[E007\]"):
        validar_parametros({"hill_climbing": {"soluciones_iniciales": 0, "iteraciones_maximas": 5}})


def test_e008_orden_entregas_invalido():
    escenario = Escenario(
        grid_size=4,
        inicio=(0, 0),
        destino=(3, 3),
        entregas=[(0, 1), (1, 1), (2, 2)],
    )
    with pytest.raises(ValueError, match=r"\[E008\]"):
        ModeloLogistico(escenario).evaluar_permuta([(0, 1), (1, 1)])
