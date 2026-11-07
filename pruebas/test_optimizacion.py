from __future__ import annotations

from pathlib import Path

from src.escenario import Escenario
from src.modelo_logistico import ModeloLogistico
from src.optimizacion.algoritmo_genetico import ejecutar_algoritmo_genetico
from src.optimizacion.recocido_simulado import recocido_simulado
from src.busqueda.busqueda_local.hill_climbing import hill_climbing

ROOT = Path(__file__).resolve().parents[1]


def test_hill_climbing():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    modelo = ModeloLogistico(escenario)
    resultado = hill_climbing(escenario.entregas, modelo, soluciones_iniciales=5, iteraciones_maximas=10, semilla=42)
    assert "mejor_costo" in resultado
    assert resultado["mejor_costo"] >= 0


def test_recocido_simulado():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    modelo = ModeloLogistico(escenario)
    resultado = recocido_simulado(modelo, escenario.entregas, temperatura_inicial=80.0, enfriamiento=0.9, iteraciones=50, semilla=42)
    assert resultado["mejor_costo"] >= 0
    assert resultado["evaluaciones"] >= 0


def test_algoritmo_genetico():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    modelo = ModeloLogistico(escenario)
    resultado = ejecutar_algoritmo_genetico(modelo, escenario.entregas, tamano_poblacion=10, generaciones=5, probabilidad_mutacion=0.2, semilla=42)
    assert resultado["mejor_costo"] >= 0
