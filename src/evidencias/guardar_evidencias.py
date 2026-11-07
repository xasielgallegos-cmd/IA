from __future__ import annotations

from src.experimentos.generar_graficas import generar_graficas


def guardar_evidencias(resultados: dict):
    if not resultados.get("run_id") or not resultados.get("modulos"):
        raise ValueError("Se requieren resultados de una ejecución real para generar evidencias.")
    return generar_graficas(resultados)
