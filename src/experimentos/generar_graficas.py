from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCIAS_DIR = ROOT / "evidencias"
DATOS_DIR = ROOT / "datos"


def _crear_directorios():
    for nombre in (
        "01_escenario",
        "02_busqueda_heuristica",
        "03_busqueda_local",
        "04_recocido_simulado",
        "05_algoritmo_genetico",
        "06_teoria_de_juegos",
        "07_minimax_alfa_beta",
        "08_integracion",
        "09_experimentos",
        "10_pruebas",
        "11_resultado_final",
    ):
        (EVIDENCIAS_DIR / nombre).mkdir(parents=True, exist_ok=True)


def _escribir_texto(destino: Path, contenido: str):
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido.rstrip() + "\n", encoding="utf-8")
    return str(destino)


def _copiar_csv(origen: Path, destino: Path, run_id: str | None = None):
    if not origen.is_file():
        return []
    if run_id is not None:
        with origen.open("r", encoding="utf-8", newline="") as archivo:
            if "run_id" not in (csv.DictReader(archivo).fieldnames or []):
                return []
        with origen.open("r", encoding="utf-8", newline="") as archivo:
            if not any(fila.get("run_id") == run_id for fila in csv.DictReader(archivo)):
                return []
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origen, destino)
    return [str(destino)]


def _corto(valor) -> str:
    if valor is None:
        return "no_disponible"
    if isinstance(valor, float) and not math.isfinite(valor):
        return "sin_solucion"
    return json.dumps(valor, ensure_ascii=False, default=str)


def _lineas_modulo(nombre: str, datos: dict, resultados: dict) -> list[str]:
    lineas = [
        f"modulo: {nombre}",
        f"estado: {datos.get('estado', 'no_ejecutado')}",
        f"run_id: {resultados['run_id']}",
        f"fecha_hora_utc: {resultados['fecha_hora']}",
        f"escenario: principal",
        f"semilla: {resultados['parametros'].get('semilla', 'no_disponible')}",
        f"parametros: {_corto(resultados['parametros'])}",
    ]
    if datos.get("mensaje_error"):
        lineas.append(f"mensaje_error: {datos['mensaje_error']}")
        return lineas
    for clave in (
        "ruta",
        "mejor_permuta",
        "costo",
        "mejor_costo",
        "valor",
        "nodos_explorados",
        "nodos_visitados",
        "nodos_podados",
        "evaluaciones",
        "iteraciones",
        "tiempo_segundos",
        "solucion_factible",
        "motivo",
        "arbol",
    ):
        if clave in datos:
            lineas.append(f"{clave}: {_corto(datos[clave])}")
    if "promedio" in datos:
        lineas.append(f"promedio_final: {_corto(datos['promedio'])}")
    if "desviacion_estandar" in datos:
        lineas.append(f"desviacion_estandar: {_corto(datos['desviacion_estandar'])}")
    if "historial_costos" in datos:
        lineas.append(f"puntos_historial: {len(datos['historial_costos'])}")
    return lineas


def _generar_escenario(resultados: dict) -> list[str]:
    escenario = resultados["escenario"]
    contenido = [
        "=== ESCENARIO LOGISTICO ===",
        f"run_id: {resultados['run_id']}",
        f"fecha_hora_utc: {resultados['fecha_hora']}",
    ]
    contenido.extend(f"{clave}: {_corto(valor)}" for clave, valor in escenario.items())
    return [_escribir_texto(EVIDENCIAS_DIR / "01_escenario" / "escenario.txt", "\n".join(contenido))]


def _generar_busqueda(resultados: dict) -> list[str]:
    rutas = []
    nombres = {"Greedy": "greedy", "A*": "a_estrella"}
    for nombre, archivo in nombres.items():
        datos = resultados["modulos"][nombre]
        contenido = ["=== BUSQUEDA HEURISTICA ===", *_lineas_modulo(nombre, datos, resultados)]
        destino = EVIDENCIAS_DIR / "02_busqueda_heuristica" / f"{archivo}.txt"
        rutas.append(_escribir_texto(destino, "\n".join(contenido)))
        if datos.get("estado") == "ok":
            rutas.extend(_copiar_csv(
                DATOS_DIR / "busqueda" / f"{archivo}.csv",
                EVIDENCIAS_DIR / "02_busqueda_heuristica" / f"resultados_{archivo}.csv",
                resultados["run_id"],
            ))

    filas = []
    for algoritmo in ("Greedy", "A*"):
        datos = resultados["modulos"][algoritmo]
        filas.append({
            "algoritmo": algoritmo,
            "ruta": _corto(datos.get("ruta")),
            "costo": datos.get("costo") if datos.get("solucion_factible") else "",
            "nodos_explorados": datos.get("nodos_explorados"),
            "tiempo_segundos": datos.get("tiempo_segundos"),
            "estado": datos.get("estado"),
            "run_id": resultados["run_id"],
        })
    ruta_csv = DATOS_DIR / "resultados_busqueda.csv"
    _guardar_csv(ruta_csv, ["algoritmo", "ruta", "costo", "nodos_explorados", "tiempo_segundos", "estado", "run_id"], filas)
    rutas.extend(_copiar_csv(ruta_csv, EVIDENCIAS_DIR / "02_busqueda_heuristica" / "resultados_busqueda.csv"))
    lineas = ["=== RESULTADOS DE BUSQUEDA ==="]
    for fila in filas:
        lineas.append(
            f"algoritmo={fila['algoritmo']} estado={fila['estado']} "
            f"costo={fila['costo'] or 'sin_solucion'} nodos={fila['nodos_explorados']} "
            f"tiempo_segundos={fila['tiempo_segundos']}"
        )
    rutas.append(_escribir_texto(EVIDENCIAS_DIR / "02_busqueda_heuristica" / "resultados_busqueda.txt", "\n".join(lineas)))
    return rutas


def _guardar_csv(path: Path, campos, filas):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def _generar_optimizacion(resultados: dict) -> list[str]:
    rutas = []
    configuraciones = (
        ("Hill Climbing", "hill_climbing", "03_busqueda_local"),
        ("Recocido simulado", "recocido_simulado", "04_recocido_simulado"),
        ("Genético", "algoritmo_genetico", "05_algoritmo_genetico"),
    )
    for nombre, archivo, carpeta in configuraciones:
        datos = resultados["modulos"][nombre]
        lineas = [f"=== {nombre.upper()} ===", *_lineas_modulo(nombre, datos, resultados)]
        rutas.append(_escribir_texto(EVIDENCIAS_DIR / carpeta / f"resultados_{archivo}.txt", "\n".join(lineas)))
        historial = datos.get("historial_costos", [])
        if historial:
            convergencia = [
                f"=== HISTORIAL REAL: {nombre} ===",
                f"run_id: {resultados['run_id']}",
                "indice,costo_mejor",
                *[f"{indice},{costo}" for indice, costo in enumerate(historial)],
            ]
            rutas.append(_escribir_texto(EVIDENCIAS_DIR / carpeta / f"convergencia_{archivo}.txt", "\n".join(convergencia)))
        csv_origen = DATOS_DIR / f"{archivo}.csv"
        if datos.get("estado") == "ok":
            rutas.extend(_copiar_csv(
                csv_origen,
                EVIDENCIAS_DIR / carpeta / f"resultados_{archivo}.csv",
                resultados["run_id"],
            ))
    return rutas


def _generar_teoria_juegos(resultados: dict) -> list[str]:
    juego = resultados["modulos"]["Teoría de juegos"]
    if juego.get("estado") == "error":
        contenido = ["=== TEORIA DE JUEGOS ===", *_lineas_modulo("Teoría de juegos", juego, resultados)]
        return [_escribir_texto(EVIDENCIAS_DIR / "06_teoria_de_juegos" / "analisis_nash.txt", "\n".join(contenido))]
    lineas = [
        "=== TEORIA DE JUEGOS ===",
        f"run_id: {resultados['run_id']}",
        "interpretacion: juego de pago comun; ambos jugadores maximizan la matriz indicada",
        "matriz_de_pagos:",
    ]
    lineas.extend(" ".join(str(valor) for valor in fila) for fila in juego["matriz"])
    lineas.append(f"mejores_respuestas: {_corto(juego['mejores_respuestas'])}")
    nash = juego["nash"]
    lineas.append(f"equilibrios_nash: {_corto(nash) if nash else 'no existe equilibrio puro'}")
    lineas.append(f"estrategias_dominantes: {_corto(juego['domina'])}")
    rutas = [_escribir_texto(EVIDENCIAS_DIR / "06_teoria_de_juegos" / "analisis_nash.txt", "\n".join(lineas))]
    rutas.extend(_copiar_csv(
        DATOS_DIR / "juego_teoria.csv",
        EVIDENCIAS_DIR / "06_teoria_de_juegos" / "matriz_pagos.csv",
        resultados["run_id"],
    ))
    return rutas


def _generar_minimax(resultados: dict) -> list[str]:
    lineas = [
        "=== MINIMAX Y ALFA-BETA ===",
        "nota: los algoritmos evaluan el arbol de decisiones de ejemplo definido en sus modulos; "
        "no es una simulacion adversaria conectada al escenario logistico.",
        f"run_id: {resultados['run_id']}",
    ]
    for nombre in ("Minimax", "Alfa-beta"):
        datos = resultados["modulos"][nombre]
        lineas.extend(_lineas_modulo(nombre, datos, resultados))
    lineas.append("equivalencia_de_valor: " + str(
        resultados["modulos"]["Minimax"].get("valor") == resultados["modulos"]["Alfa-beta"].get("valor")
    ))
    txt = _escribir_texto(EVIDENCIAS_DIR / "07_minimax_alfa_beta" / "resultados_minimax.txt", "\n".join(lineas))
    csv_path = DATOS_DIR / "minimax.csv"
    csv_rows = [
        {
            "algoritmo": nombre,
            "valor": resultados["modulos"][nombre].get("valor"),
            "nodos_visitados": resultados["modulos"][nombre].get("nodos_visitados"),
            "nodos_podados": resultados["modulos"][nombre].get("nodos_podados"),
            "estado": resultados["modulos"][nombre].get("estado"),
            "run_id": resultados["run_id"],
        }
        for nombre in ("Minimax", "Alfa-beta")
    ]
    _guardar_csv(csv_path, ["algoritmo", "valor", "nodos_visitados", "nodos_podados", "estado", "run_id"], csv_rows)
    return [txt, *_copiar_csv(csv_path, EVIDENCIAS_DIR / "07_minimax_alfa_beta" / "resultados_minimax.csv")]


def _generar_integracion(resultados: dict) -> list[str]:
    integration_path = DATOS_DIR / "registro_integracion.csv"
    destino_csv = EVIDENCIAS_DIR / "08_integracion" / "resumen_ejecucion.csv"
    rutas = _copiar_csv(integration_path, destino_csv)
    lineas = [
        "=== ESTADO DE INTEGRACION ===",
        f"run_id: {resultados['run_id']}",
        f"fecha_hora_utc: {resultados['fecha_hora']}",
    ]
    for registro in resultados["registros"]:
        lineas.append(
            f"modulo={registro['modulo']} estado={registro['estado']} "
            f"resultado={registro['resultado']} mensaje_error={registro['mensaje_error'] or 'ninguno'}"
        )
    rutas.append(_escribir_texto(EVIDENCIAS_DIR / "08_integracion" / "resumen_ejecucion.txt", "\n".join(lineas)))
    return rutas


def _generar_resumenes(resultados: dict) -> list[str]:
    datos = resultados["resultados"]
    lineas = [
        "=== ESTADISTICAS DE LA EJECUCION ===",
        f"run_id: {resultados['run_id']}",
        "cantidad_corridas_por_algoritmo: 1",
        "La media corresponde al unico resultado de esta ejecucion; "
        "la desviacion estandar muestral requiere al menos dos corridas.",
    ]
    rutas = [
        fila for fila in datos
        if fila["algoritmo"] in {"Greedy", "A*"} and fila["costo"] is not None
    ]
    optimizaciones = [
        fila for fila in datos
        if fila["algoritmo"] in {"Hill Climbing", "Recocido simulado", "Genético"}
        and fila["costo"] is not None
    ]
    if rutas:
        mejor_ruta = min(rutas, key=lambda fila: fila["costo"])
        lineas.append(f"mejor_ruta_encontrada: {mejor_ruta['algoritmo']} costo={mejor_ruta['costo']}")
    if optimizaciones:
        mejor_orden = min(optimizaciones, key=lambda fila: fila["costo"])
        lineas.append(
            f"mejor_orden_de_entregas_encontrado: {mejor_orden['algoritmo']} "
            f"costo={mejor_orden['costo']}"
        )
    for fila in datos:
        costo = fila["costo"]
        metrica = f"costo={costo}" if costo is not None else (
            f"valor={fila['valor']}" if fila.get("valor") is not None else "resultado=no_disponible"
        )
        promedio_corridas = costo if costo is not None else "no_aplicable"
        lineas.append(
            f"algoritmo={fila['algoritmo']} estado={fila['estado']} "
            f"{metrica} "
            f"media_corridas_n=1:{promedio_corridas} "
            "desviacion_estandar_corridas=no_aplicable "
            f"promedio_interno={fila['promedio_interno']} "
            f"desviacion_estandar_interna={fila['desviacion_estandar_interna']} "
            f"tiempo_segundos={fila['tiempo_segundos']} "
            f"nodos_evaluados={fila['nodos_explorados']} "
            f"corridas_exitosas={fila['corridas_exitosas']} corridas_fallidas={fila['corridas_fallidas']}"
        )
    resumen = _escribir_texto(EVIDENCIAS_DIR / "09_experimentos" / "estadisticas_experimentos.txt", "\n".join(lineas))
    final = _escribir_texto(EVIDENCIAS_DIR / "11_resultado_final" / "resumen_general.txt", "\n".join(lineas))
    return [resumen, final]


def generar_graficas(resultados: dict):
    _crear_directorios()
    rutas = []
    rutas.extend(_generar_escenario(resultados))
    rutas.extend(_generar_busqueda(resultados))
    rutas.extend(_generar_optimizacion(resultados))
    rutas.extend(_generar_teoria_juegos(resultados))
    rutas.extend(_generar_minimax(resultados))
    rutas.extend(_generar_integracion(resultados))
    rutas.extend(_generar_resumenes(resultados))
    resumen = _escribir_texto(EVIDENCIAS_DIR / "resumen_evidencias.txt", "\n".join(rutas))
    rutas.append(resumen)
    return rutas
