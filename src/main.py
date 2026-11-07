from __future__ import annotations

import json
from pathlib import Path

from src.escenario import Escenario
from src.evidencias.guardar_evidencias import guardar_evidencias
from src.experimentos.ejecutar_experimentos import ejecutar_experimentos
from src.validaciones import validar_escenario


ROOT = Path(__file__).resolve().parents[1]


def main():
    escenario = Escenario.desde_json(ROOT / "configuracion" / "escenario.json")
    escenario.cargar_costos_desde_csv(ROOT / "configuracion" / "costos_movimiento.csv")
    validar_escenario(escenario)

    with (ROOT / "configuracion" / "parametros.json").open("r", encoding="utf-8") as archivo:
        parametros = json.load(archivo)

    resultados = ejecutar_experimentos(escenario, parametros)
    rutas = guardar_evidencias(resultados)

    errores = [registro for registro in resultados["registros"] if registro["estado"] == "error"]
    sin_solucion = [registro for registro in resultados["registros"] if registro["estado"] == "sin_solucion"]
    if errores:
        raise RuntimeError(
            "Fallaron módulos; consulte evidencias/08_integracion/resumen_ejecucion.csv: "
            + ", ".join(registro["modulo"] for registro in errores)
        )
    print("Ejecución finalizada." if not sin_solucion else "Ejecución finalizada con módulos sin solución.")
    costos_ruta = [
        resultado["costo"]
        for resultado in resultados["resultados"]
        if resultado["algoritmo"] in {"Greedy", "A*"} and resultado["costo"] is not None
    ]
    print(f"Mejor costo entre rutas encontradas: {min(costos_ruta) if costos_ruta else 'sin solución'}")
    print(f"Resultados guardados en: {ROOT / 'datos'} y {ROOT / 'evidencias'}")
    print(f"Evidencias actualizadas: {len(rutas)}")


if __name__ == "__main__":
    main()
