from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCIAS_DIR = ROOT / "evidencias" / "10_pruebas"
_RESUMEN = re.compile(r"(?P<count>\d+) (?P<kind>passed|failed|skipped|error|errors|xfailed|xpassed)")


def registrar_resultado_pruebas() -> int:
    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True,
        text=True,
        check=False,
    )
    salida = (resultado.stdout or "") + (resultado.stderr or "")
    conteos = {
        "aprobadas": 0,
        "fallidas": 0,
        "omitidas": 0,
        "errores": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    claves = {
        "passed": "aprobadas",
        "failed": "fallidas",
        "skipped": "omitidas",
        "error": "errores",
        "errors": "errores",
        "xfailed": "xfailed",
        "xpassed": "xpassed",
    }
    for coincidencia in _RESUMEN.finditer(salida):
        conteos[claves[coincidencia.group("kind")]] += int(coincidencia.group("count"))
    total = sum(conteos.values())
    estado = (
        "OK"
        if resultado.returncode == 0 and total > 0 and not conteos["fallidas"] and not conteos["errores"]
        else "REVISAR"
    )

    EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
    contenido = [
        f"codigo_salida_pytest: {resultado.returncode}",
        f"estado: {estado}",
        "--- salida real de pytest ---",
        salida.rstrip() or "(sin salida)",
    ]
    (EVIDENCIAS_DIR / "resultado_pruebas.txt").write_text("\n".join(contenido) + "\n", encoding="utf-8")
    with (EVIDENCIAS_DIR / "resumen_pruebas.csv").open("w", newline="", encoding="utf-8") as archivo:
        campos = ["total", "aprobadas", "fallidas", "omitidas", "errores", "xfailed", "xpassed", "codigo_salida", "resultado"]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerow({
            "total": total,
            **conteos,
            "codigo_salida": resultado.returncode,
            "resultado": estado,
        })
    return resultado.returncode


if __name__ == "__main__":
    raise SystemExit(registrar_resultado_pruebas())
