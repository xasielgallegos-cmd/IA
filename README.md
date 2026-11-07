# Diseño e implementación

## Arquitectura

`src/main.py` coordina la lectura de configuración, validaciones, ejecución y generación de evidencias. El escenario compartido se representa con `Escenario`; `ModeloLogistico` evalúa secuencias de entregas concatenando el inicio, cada entrega y el destino. Los experimentos registran tanto resultados por algoritmo como filas de estado por módulo.

La generación de evidencia es una fase de presentación que recibe el objeto de resultados de la corrida actual. No vuelve a calcular algoritmos ni ejecuta pruebas. Los CSV originales conservan los datos; los TXT hacen legible el resumen y registran el mismo `run_id`.

## Búsqueda y costos

La cuadrícula utiliza movimientos ortogonales. En `costos_movimiento.csv`, cada fila asigna el costo de entrada a una celda; si no hay una entrada para la celda, el paso cuesta una unidad. Obstáculos no son transitables.

Greedy prioriza la distancia Manhattan y devuelve una ruta válida si encuentra una, sin garantía de optimalidad. A* usa el costo acumulado más una Manhattan admisible escalada por el mínimo costo de movimiento positivo de la configuración. Los costos inválidos se rechazan.

## Optimización de entregas

`ModeloLogistico.evaluar_permuta` verifica que la permutación contenga todas las entregas requeridas exactamente una vez. Evalúa cada segmento con A* y suma su costo. Hill Climbing intercambia pares; recocido simulado aplica aceptación probabilística; el algoritmo genético realiza selección, cruce y mutación. Cada optimizador recibe la semilla configurada. Sus conteos de evaluación reflejan las evaluaciones realizadas y sus historiales se escriben como CSV.

La configuración contiene recursos y restricciones nominales, pero aún no especifica consumo de recursos por tramo, presupuesto ni demanda de cada entrega. No se restringe la ruta por combustible/capacidad hasta que esas unidades/reglas estén definidas.

## Teoría de juegos y adversarios

La matriz de pagos actual es de pago común: ambos jugadores maximizan la misma celda. Las mejores respuestas se derivan de filas y columnas y Nash es su intersección. La matriz puede provenir de `parametros.json`; las evidencias registran la matriz usada y el análisis calculado.

Minimax y alfa-beta procesan el árbol estático contenido en sus módulos. Alfa-beta usa los mismos valores y orden de ramas que Minimax, produciendo el mismo valor y visitando no más nodos en el caso configurado. El árbol es didáctico: no se conecta a los recursos, rutas ni decisiones de un competidor definidos en el escenario.

## Ejecuciones y reproducibilidad

Cada invocación del sistema crea un identificador y hora UTC. Los CSV de resumen relacionan algoritmo, escenario, semilla, parámetros, estado, costo, tiempo y métricas. `registro_integracion.csv` y `registro_ejecuciones.csv` son acumulativos para preservar el historial; se rechaza un esquema incompatible en lugar de sobrescribir el archivo. Los CSV de detalle describen la corrida más reciente.

El protocolo actual realiza una ejecución por algoritmo y por escenario principal. Una desviación estándar muestral entre corridas no se calcula con una sola corrida. Las desviaciones internas informadas por optimizadores se refieren a sus propias muestras de búsqueda y no se confunden con estadísticas de ejecuciones independientes.

## Errores E001–E008

| Código | Condición validada |
|---|---|
| E001 | Falta el archivo de escenario |
| E002 | JSON inválido o raíz JSON no es un objeto |
| E003 | Coordenada inválida, fuera de cuadrícula o entregas duplicadas |
| E004 | Inicio, destino o entrega sobre un obstáculo |
| E005 | Recurso solicitado no declarado o disponible insuficiente para un requerimiento explícito |
| E006 | No existe ruta entre los puntos de un tramo |
| E007 | Parámetros, costos de movimiento o matriz de pagos inválidos |
| E008 | Una secuencia no contiene cada entrega exactamente una vez |

E005 se puede comprobar cuando se proporciona un diccionario explícito de requerimientos; el escenario actual no declara requerimientos de combustible/transporte por ruta.

## Pruebas y evidencias de pruebas

Las pruebas usan Pytest y se ejecutan independientemente:

```bash
PYTHONPATH=. python3 -m pytest -q
```

El comando `python3 -m src.evidencias.registrar_pruebas` ejecuta la suite, guarda la salida real, conteos y código de salida. El programa principal no lanza Pytest ni altera los resultados de la suite.

## Limitaciones pendientes

- Solo se configura un escenario y una corrida externa por algoritmo; no hay barrido de escenarios ni protocolo de repeticiones.
- No están formalizadas las unidades de recursos, presupuesto, capacidad ni su consumo.
- El juego tiene una sola matriz común; no modela pagos independientes para dos jugadores.
- El árbol de Minimax/alfa-beta es un ejemplo independiente del sistema logístico.
- Las estadísticas entre corridas son limitadas mientras no se defina cuántas repeticiones deben realizarse.
