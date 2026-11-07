# Manual de usuario

## Preparación

Se requiere Python 3.11 o posterior y Pytest para ejecutar las pruebas. Desde la raíz:

```bash
python3 -m pip install -r requirements.txt
```

El programa no requiere Matplotlib porque sus evidencias actuales son texto y CSV.

## Ejecutar el sistema

```bash
PYTHONPATH=. python3 -m src.main
```

El proceso carga `configuracion/escenario.json`, los costos de `configuracion/costos_movimiento.csv` y los parámetros de `configuracion/parametros.json`. Valida las entradas, ejecuta los módulos, escribe resultados en `datos/` y actualiza las evidencias TXT/CSV en `evidencias/`.

Cada corrida asigna un `run_id`. Los CSV de resultados incluyen ese identificador y hora UTC para relacionarlos con sus evidencias. `datos/registro_integracion.csv` y `datos/registro_ejecuciones.csv` son acumulativos y conservan filas por módulo y corrida. Sus estados indican `ok`, `sin_solucion` o `error`. Si un módulo falla, se registra el error y el programa termina con una excepción después de generar los archivos de evidencia posibles.

## Ejecutar pruebas y registrar su salida

Las pruebas son independientes de la ejecución normal del sistema:

```bash
PYTHONPATH=. python3 -m pytest -q
```

Para volver a ejecutar Pytest y conservar su salida, conteos y código de salida:

```bash
PYTHONPATH=. python3 -m src.evidencias.registrar_pruebas
```

El registrador no se invoca desde `src.main`. Su CSV marca `OK` solo cuando Pytest devuelve código cero, se detectó un resumen de pruebas y no se reportan fallos o errores.

## Archivos de configuración

- `configuracion/escenario.json`: tamaño de cuadrícula, inicio, destino, entregas, obstáculos, recursos y restricciones declarados.
- `configuracion/costos_movimiento.csv`: costo de entrar en cada celda.
- `configuracion/parametros.json`: semilla y parámetros de búsqueda, optimizadores, matriz de pagos y profundidad adversaria.

Para no inventar semántica, los recursos de combustible/transporte y capacidad no se comparan contra costos o demandas: la configuración no define esas unidades ni demandas por entrega.

## Resultados y evidencias

- `datos/resultados_experimentos.csv`: resumen de la corrida actual con parámetros, semilla, estado, costo, tiempo y métricas disponibles.
- `datos/busqueda/`: rutas CSV detalladas de Greedy y A*.
- Los CSV de optimización registran las curvas de mejor costo con metadatos de corrida.
- `datos/juego_teoria.csv`: matriz de pagos completa utilizada.
- `datos/minimax.csv`: valor y nodos visitados por Minimax y alfa-beta.
- `datos/registro_integracion.csv`: historial de ejecución por módulo.
- `evidencias/01_escenario/` a `evidencias/11_resultado_final/`: resúmenes TXT y copias CSV pertinentes.
- `evidencias/10_pruebas/`: resultado real, actualizado únicamente al ejecutar el registrador de Pytest.

La configuración actual ejecuta una corrida por algoritmo. La desviación estándar entre corridas requiere como mínimo dos ejecuciones y, por tanto, se identifica como no disponible; no se sustituye por cero.

## Errores de validación

El sistema utiliza códigos E001–E008 para archivo faltante, JSON incorrecto, coordenadas, obstáculos, recursos, rutas inexistentes, parámetros/costos/matriz inválidos y orden de entregas inválido. Una búsqueda sin ruta no crea una ruta ficticia: registra ausencia de solución y su motivo.

## Alcance de los algoritmos

Greedy genera una ruta heurística, pero no garantiza costo mínimo. A* considera los costos configurados. Los optimizadores buscan órdenes de visita para todas las entregas. La teoría de juegos actual supone que ambos jugadores maximizan la misma matriz de pagos. Minimax y alfa-beta operan en un árbol de ejemplo y no representan decisiones adversarias conectadas a la ruta logística.
