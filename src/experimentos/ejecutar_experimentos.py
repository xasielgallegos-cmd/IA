from __future__ import annotations

import csv
import json
import math
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.adversarios.alfa_beta import evaluar_alfa_beta
from src.adversarios.minimax import evaluar_minimax
from src.busqueda.a_estrella import a_estrella_busqueda
from src.busqueda.greedy import greedy_best_first_search
from src.busqueda.busqueda_local.hill_climbing import hill_climbing
from src.modelo_logistico import ModeloLogistico
from src.optimizacion.algoritmo_genetico import ejecutar_algoritmo_genetico
from src.optimizacion.recocido_simulado import recocido_simulado
from src.teoria_juegos.estrategias import analizar_juego_logistico
from src.validaciones import validar_parametros


BASE_DIR = Path(__file__).resolve().parents[2]
DATOS_DIR = BASE_DIR / "datos"
BUSQUEDA_DIR = DATOS_DIR / "busqueda"


def _guardar_csv(path: Path, fieldnames, filas):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=fieldnames)
        escritor.writeheader()
        escritor.writerows(filas)


def _anexar_csv(path: Path, fieldnames, filas):
    path.parent.mkdir(parents=True, exist_ok=True)
    existe = path.exists() and path.stat().st_size > 0
    if existe:
        with path.open("r", newline="", encoding="utf-8") as archivo:
            campos_existentes = csv.DictReader(archivo).fieldnames
        if campos_existentes != fieldnames:
            raise ValueError(f"El esquema histórico de {path} no coincide; no se sobrescribió.")
    with path.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=fieldnames)
        if not existe:
            escritor.writeheader()
        escritor.writerows(filas)


def _json(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str, sort_keys=True)


def _registrar(
    nombre: str,
    funcion,
    run_id: str,
    fecha_hora: str,
    detalles: dict,
    integracion: list[dict],
):
    inicio = time.perf_counter()
    try:
        datos = funcion()
        duracion = time.perf_counter() - inicio
        datos.setdefault("tiempo_segundos", duracion)
        estado = "sin_solucion" if datos.get("solucion_factible") is False else "ok"
        mensaje = datos.get("motivo", "")
        if estado == "sin_solucion" and not mensaje:
            mensaje = "[E006] El algoritmo terminó sin encontrar una solución."
            datos["motivo"] = mensaje
    except Exception as error:
        duracion = time.perf_counter() - inicio
        sin_solucion = isinstance(error, ValueError) and str(error).startswith("[E006]")
        datos = {
            "estado": "sin_solucion" if sin_solucion else "error",
            "solucion_factible": False,
            "motivo": f"{type(error).__name__}: {error}",
            "tiempo_segundos": duracion,
        }
        estado = datos["estado"]
        mensaje = datos["motivo"] if sin_solucion else f"{type(error).__name__}: {error}"
        if not sin_solucion:
            datos["mensaje_error"] = mensaje

    datos["estado"] = estado
    detalles[nombre] = datos
    integracion.append({
        "run_id": run_id,
        "fecha_hora": fecha_hora,
        "modulo": nombre,
        "estado": estado,
        "resultado": _json(_resumen_modulo(datos)),
        "mensaje_error": mensaje,
    })
    return datos


def _resumen_modulo(datos: dict) -> dict:
    if "mensaje_error" in datos:
        return {"error": datos["mensaje_error"]}
    return {
        clave: datos.get(clave)
        for clave in (
            "costo",
            "mejor_costo",
            "valor",
            "nodos_explorados",
            "nodos_visitados",
            "nodos_podados",
            "evaluaciones",
            "equilibrios_nash",
            "solucion_factible",
            "motivo",
            "promedio",
            "desviacion_estandar",
        )
        if clave in datos
    }


def _agregar_resultado(resultados: list[dict], algoritmo: str, datos: dict, clave_costo="costo"):
    costo = datos.get(clave_costo)
    if isinstance(costo, float) and not math.isfinite(costo):
        costo = None
    nodos = datos.get("nodos_explorados", datos.get("nodos_visitados", datos.get("evaluaciones")))
    resultados.append({
        "algoritmo": algoritmo,
        "costo": costo,
        "valor": datos.get("valor"),
        "nodos_explorados": nodos,
        "tiempo_segundos": datos.get("tiempo_segundos"),
        "promedio_interno": datos.get("promedio"),
        "desviacion_estandar_interna": datos.get("desviacion_estandar"),
        "promedio_corridas": costo,
        "desviacion_estandar_corridas": None,
        "corridas_exitosas": int(datos.get("estado") == "ok"),
        "corridas_fallidas": int(datos.get("estado") != "ok"),
        "estado": datos["estado"],
        "solucion_factible": datos.get("solucion_factible"),
        "mensaje_error": datos.get("mensaje_error", datos.get("motivo", "")),
    })


def _guardar_registro_integracion(filas: list[dict]):
    path = DATOS_DIR / "registro_integracion.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    existe = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as archivo:
        campos = ["run_id", "fecha_hora", "modulo", "estado", "resultado", "mensaje_error"]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        escritor.writerows(filas)


def ejecutar_experimentos(escenario, parametros):
    validar_parametros(parametros)
    run_id = uuid.uuid4().hex
    fecha_hora = datetime.now(timezone.utc).isoformat()
    modelo = ModeloLogistico(escenario)
    entregas = escenario.entregas
    resultados: list[dict] = []
    registros: list[dict] = []
    detalles: dict[str, dict] = {}

    def ejecutar_busqueda(nombre, algoritmo):
        inicio = time.perf_counter()
        ruta, costo, nodos = algoritmo(
            escenario.inicio,
            escenario.destino,
            escenario.obstaculos,
            escenario.grid_size,
            escenario.costos_movimiento,
        )
        tiempo = time.perf_counter() - inicio
        factible = ruta is not None
        datos = {
            "ruta": ruta,
            "costo": costo,
            "nodos_explorados": nodos,
            "solucion_factible": factible,
            "algoritmo": nombre,
            "tiempo_segundos": tiempo,
        }
        nombre_archivo = "a_estrella.csv" if nombre == "A*" else "greedy.csv"
        _guardar_csv(
            BUSQUEDA_DIR / nombre_archivo,
            ["run_id", "fecha_hora", "semilla", "parametros", "ruta", "costo", "nodos_explorados", "tiempo_segundos", "solucion_factible"],
            [{
                "run_id": run_id,
                "fecha_hora": fecha_hora,
                "semilla": parametros.get("semilla", 42),
                "parametros": _json(parametros),
                "ruta": _json(ruta) if ruta is not None else "",
                "costo": costo if factible else "",
                "nodos_explorados": nodos,
                "tiempo_segundos": tiempo,
                "solucion_factible": factible,
            }],
        )
        return datos

    for nombre, algoritmo in (
        ("Greedy", greedy_best_first_search),
        ("A*", a_estrella_busqueda),
    ):
        datos = _registrar(
            nombre,
            lambda nombre=nombre, algoritmo=algoritmo: ejecutar_busqueda(nombre, algoritmo),
            run_id,
            fecha_hora,
            detalles,
            registros,
        )
        _agregar_resultado(resultados, nombre, datos)

    def ejecutar_hill_climbing():
        datos = hill_climbing(
            entregas,
            modelo,
            soluciones_iniciales=parametros.get("hill_climbing", {}).get("soluciones_iniciales", 10),
            iteraciones_maximas=parametros.get("hill_climbing", {}).get("iteraciones_maximas", 50),
            semilla=parametros.get("semilla", 42),
        )
        datos["solucion_factible"] = math.isfinite(datos["mejor_costo"])
        _guardar_csv(
            DATOS_DIR / "hill_climbing.csv",
            ["run_id", "fecha_hora", "semilla", "parametros", "iteracion", "costo"],
            [
                {
                    "run_id": run_id,
                    "fecha_hora": fecha_hora,
                    "semilla": parametros.get("semilla", 42),
                    "parametros": _json(parametros),
                    "iteracion": indice,
                    "costo": costo,
                }
                for indice, costo in enumerate(datos["historial_costos"])
            ],
        )
        return datos

    hill = _registrar("Hill Climbing", ejecutar_hill_climbing, run_id, fecha_hora, detalles, registros)
    _agregar_resultado(resultados, "Hill Climbing", hill, "mejor_costo")

    def ejecutar_recocido():
        datos = recocido_simulado(
            modelo,
            entregas,
            temperatura_inicial=parametros.get("recocido_simulado", {}).get("temperatura_inicial", 120.0),
            enfriamiento=parametros.get("recocido_simulado", {}).get("enfriamiento", 0.95),
            iteraciones=parametros.get("recocido_simulado", {}).get("iteraciones", 250),
            semilla=parametros.get("semilla", 42),
        )
        datos["solucion_factible"] = math.isfinite(datos["mejor_costo"])
        _guardar_csv(
            DATOS_DIR / "recocido_simulado.csv",
            ["run_id", "fecha_hora", "semilla", "parametros", "iteracion", "costo"],
            [
                {
                    "run_id": run_id,
                    "fecha_hora": fecha_hora,
                    "semilla": parametros.get("semilla", 42),
                    "parametros": _json(parametros),
                    "iteracion": indice,
                    "costo": costo,
                }
                for indice, costo in enumerate(datos["historial_costos"])
            ],
        )
        return datos

    recocido = _registrar("Recocido simulado", ejecutar_recocido, run_id, fecha_hora, detalles, registros)
    _agregar_resultado(resultados, "Recocido simulado", recocido, "mejor_costo")

    def ejecutar_genetico():
        datos = ejecutar_algoritmo_genetico(
            modelo,
            entregas,
            tamano_poblacion=parametros.get("algoritmo_genetico", {}).get("tamano_poblacion", 20),
            generaciones=parametros.get("algoritmo_genetico", {}).get("generaciones", 35),
            probabilidad_mutacion=parametros.get("algoritmo_genetico", {}).get("probabilidad_mutacion", 0.15),
            semilla=parametros.get("semilla", 42),
        )
        datos["solucion_factible"] = math.isfinite(datos["mejor_costo"])
        _guardar_csv(
            DATOS_DIR / "algoritmo_genetico.csv",
            ["run_id", "fecha_hora", "semilla", "parametros", "iteracion", "costo"],
            [
                {
                    "run_id": run_id,
                    "fecha_hora": fecha_hora,
                    "semilla": parametros.get("semilla", 42),
                    "parametros": _json(parametros),
                    "iteracion": indice,
                    "costo": costo,
                }
                for indice, costo in enumerate(datos["historial_costos"])
            ],
        )
        return datos

    genetico = _registrar("Genético", ejecutar_genetico, run_id, fecha_hora, detalles, registros)
    _agregar_resultado(resultados, "Genético", genetico, "mejor_costo")

    def ejecutar_teoria_juegos():
        matriz = parametros.get("teoria_juegos", {}).get("matriz_pagos")
        datos = analizar_juego_logistico(matriz)
        datos["solucion_factible"] = True
        datos["equilibrios_nash"] = datos["nash"]
        _guardar_csv(
            DATOS_DIR / "juego_teoria.csv",
            ["run_id", "fila", "columna", "pago"],
            [
                {"run_id": run_id, "fila": fila, "columna": columna, "pago": valor}
                for fila, pagos in enumerate(datos["matriz"])
                for columna, valor in enumerate(pagos)
            ],
        )
        return datos

    juego = _registrar("Teoría de juegos", ejecutar_teoria_juegos, run_id, fecha_hora, detalles, registros)
    _agregar_resultado(resultados, "Teoría de juegos", juego)

    profundidad = parametros.get("minimax", {}).get("profundidad", 3)
    for nombre, evaluador in (
        ("Minimax", lambda: evaluar_minimax(profundidad)),
        ("Alfa-beta", lambda: evaluar_alfa_beta(profundidad)),
    ):
        datos = _registrar(
            nombre,
            evaluador,
            run_id,
            fecha_hora,
            detalles,
            registros,
        )
        if datos.get("estado") != "error":
            datos["solucion_factible"] = True
        _agregar_resultado(resultados, nombre, datos)

    _guardar_csv(
        DATOS_DIR / "resultados_experimentos.csv",
        [
            "run_id",
            "fecha_hora",
            "algoritmo",
            "escenario",
            "semilla",
            "parametros",
            "estado",
            "resultado",
            "costo",
            "valor",
            "tiempo_segundos",
            "nodos_explorados",
            "promedio_interno",
            "desviacion_estandar_interna",
            "promedio_corridas",
            "desviacion_estandar_corridas",
            "corridas_exitosas",
            "corridas_fallidas",
            "solucion_factible",
            "mensaje_error",
        ],
        [
            {
                **fila,
                "run_id": run_id,
                "fecha_hora": fecha_hora,
                "escenario": "principal",
                "semilla": parametros.get("semilla", 42),
                "parametros": _json(parametros),
                "resultado": _json(_resumen_modulo(detalles[fila["algoritmo"]])),
            }
            for fila in resultados
        ],
    )
    _anexar_csv(
        DATOS_DIR / "registro_ejecuciones.csv",
        ["run_id", "fecha_hora", "algoritmo", "escenario", "valor", "tiempo_segundos", "estado"],
        [
            {
                "run_id": fila["run_id"],
                "fecha_hora": fila["fecha_hora"],
                "algoritmo": fila["modulo"],
                "escenario": "principal",
                "valor": _json(_resumen_modulo(detalles[fila["modulo"]])),
                "tiempo_segundos": detalles[fila["modulo"]].get("tiempo_segundos"),
                "estado": fila["estado"],
            }
            for fila in registros
        ],
    )
    _guardar_csv(
        DATOS_DIR / "escenarios.csv",
        ["run_id", "escenario", "inicio", "destino", "entregas", "obstaculos"],
        [{
            "run_id": run_id,
            "escenario": "principal",
            "inicio": _json(escenario.inicio),
            "destino": _json(escenario.destino),
            "entregas": _json(escenario.entregas),
            "obstaculos": _json(sorted(escenario.obstaculos)),
        }],
    )
    _guardar_registro_integracion(registros)

    return {
        "run_id": run_id,
        "fecha_hora": fecha_hora,
        "escenario": escenario.to_dict(),
        "parametros": parametros,
        "resultados": resultados,
        "registros": registros,
        "modulos": detalles,
        "juego": juego,
        "minimax": detalles.get("Minimax"),
        "alfa_beta": detalles.get("Alfa-beta"),
        "busqueda": {
            "greedy": detalles.get("Greedy", {}).get("ruta"),
            "a_estrella": detalles.get("A*", {}).get("ruta"),
        },
        "hill_climbing": hill,
        "recocido_simulado": recocido,
        "algoritmo_genetico": genetico,
    }
