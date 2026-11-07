# SISTEMA_LOGISTICO_IA

Sistema académico local para experimentar con búsqueda de rutas en cuadrícula, optimización del orden de entregas, una matriz de pagos y búsqueda adversaria en un árbol de ejemplo. Los resultados se calculan durante cada ejecución; los archivos bajo `datos/` son CSV y las evidencias bajo `evidencias/` son texto y CSV.

## Requisitos

- Python 3.11 o posterior.
- Pytest para ejecutar las pruebas.

No se requiere Matplotlib: el formato de evidencia vigente es TXT/CSV.

## Léeme: instrucciones de ejecución en macOS

Abre Terminal y entra a la carpeta del proyecto:

```bash
cd /Users/Xas/Downloads/p
```

### 1. Preparar el entorno (solo la primera vez)

Se recomienda crear y activar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala los requisitos del proyecto:

```bash
python -m pip install -r requirements.txt
```

Si ya tienes un entorno virtual, actívalo antes de ejecutar los comandos. En macOS, si el comando `python3` no está disponible, instala Python 3 y vuelve a abrir Terminal.

### 2. Ejecutar el sistema

Desde la raíz del proyecto:

```bash
PYTHONPATH=. python3 -m src.main
```

El programa ejecuta los algoritmos y actualiza sus resultados en `datos/` y las evidencias TXT/CSV en `evidencias/`. Para ejecutarlo de nuevo, usa el mismo comando. Cada corrida genera un identificador nuevo; los archivos de resumen reflejan la corrida más reciente y los registros de integración conservan las corridas anteriores.

### 3. Ejecutar las pruebas

```bash
PYTHONPATH=. python3 -m pytest -q
```

### 4. Guardar la evidencia de las pruebas

Este comando vuelve a ejecutar Pytest y guarda su salida real, conteos y código de salida:

```bash
PYTHONPATH=. python3 -m src.evidencias.registrar_pruebas
```

Los resultados quedan en:

- `evidencias/10_pruebas/resultado_pruebas.txt`
- `evidencias/10_pruebas/resumen_pruebas.csv`

Las pruebas son independientes: no se ejecutan al iniciar `src.main`.

### Ejecución rápida después de la preparación

Para una corrida normal:

```bash
cd /Users/Xas/Downloads/p
PYTHONPATH=. python3 -m src.main
```

Para validar el proyecto y actualizar la evidencia de Pytest:

```bash
cd /Users/Xas/Downloads/p
PYTHONPATH=. python3 -m pytest -q
PYTHONPATH=. python3 -m src.evidencias.registrar_pruebas
```

## Flujo y componentes

1. `src/main.py` carga JSON/CSV de configuración, valida escenario y parámetros, llama a los experimentos y genera evidencias.
2. `src/escenario.py` representa la cuadrícula, los puntos, obstáculos y costos de entrada a celdas.
3. `src/busqueda/greedy.py` ejecuta Greedy Best-First Search. Es heurístico y no garantiza el menor costo.
4. `src/busqueda/a_estrella.py` ejecuta A* con costo acumulado y distancia Manhattan escalada por el menor costo de movimiento.
5. `src/modelo_logistico.py` evalúa recorridos que incluyen cada entrega exactamente una vez, en un orden dado, y terminan en el destino.
6. Hill Climbing, recocido simulado y el algoritmo genético buscan permutaciones de las entregas. La semilla y los parámetros vienen de `configuracion/parametros.json`.
7. `src/teoria_juegos/estrategias.py` analiza una matriz de pago común: ambos jugadores maximizan la misma matriz. Sus mejores respuestas y equilibrios se calculan, no se escriben como resultados fijos.
8. Minimax y alfa-beta evalúan un árbol pequeño definido en sus módulos. Es un ejemplo de búsqueda adversaria y no está conectado a la planificación logística.
9. `src/experimentos/ejecutar_experimentos.py` genera CSV de resultados y añade registros reales a `datos/registro_integracion.csv`.
10. `src/experimentos/generar_graficas.py` (nombre conservado por compatibilidad) produce TXT y copia CSV de esa corrida.

## Salidas

- `datos/resultados_experimentos.csv`: resumen de la corrida actual, con ID, fecha, parámetros, semilla, estado, costo, tiempo y métricas disponibles.
- `datos/busqueda/`: rutas y métricas detalladas de Greedy y A*.
- `datos/hill_climbing.csv`, `datos/recocido_simulado.csv`, `datos/algoritmo_genetico.csv`: historiales generados por los algoritmos y metadatos de la corrida.
- `datos/juego_teoria.csv`: pagos de la matriz analizada.
- `datos/minimax.csv`: valor y nodos de los dos métodos adversarios.
- `datos/registro_integracion.csv` y `datos/registro_ejecuciones.csv`: historial acumulativo por módulo y corrida; no se sobrescriben al ejecutar de nuevo.
- `evidencias/`: resúmenes TXT y copias de presentación CSV. No se generan PNG.

Una ejecución actualiza los CSV de resultados y los TXT correspondientes. El CSV acumulativo de integración conserva corridas previas. En el diseño vigente se realiza una corrida por algoritmo en un solo escenario; por eso la desviación estándar muestral entre corridas se reporta como no aplicable. Las métricas estadísticas internas de los optimizadores se etiquetan separadamente.

## Validaciones y límites conocidos

- E001: archivo del escenario faltante.
- E002: JSON de escenario inválido.
- E003: coordenadas inválidas/fuera de límites o entregas duplicadas.
- E004: inicio, destino o entrega sobre un obstáculo.
- E005: recurso solicitado no definido o cantidad disponible insuficiente, cuando se proporciona un requerimiento explícito.
- E006: no existe ruta; la búsqueda devuelve `None` e infinito, y el modelo logístico identifica el tramo sin solución.
- E007: parámetros, costos de movimiento o matriz de pagos inválidos.
- E008: orden de entregas inválido (no contiene cada entrega exactamente una vez).

El escenario declara recursos y restricciones, pero no define consumo de combustible por movimiento ni una demanda de recursos por entrega. Por ello, esos campos aún no actúan como restricciones del costo de ruta; no se atribuye al modelo una factibilidad de combustible/capacidad que no pueda calcular con la configuración actual.

No se especificó un protocolo con varias repeticiones por algoritmo. El proyecto informa resultados de una corrida reproducible mediante semilla, pero no presenta esa corrida única como un análisis estadístico de múltiples ejecuciones.
