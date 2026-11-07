from __future__ import annotations

from src.adversarios.alfa_beta import alfa_beta, construir_arbol as construir_arbol_alfa
from src.adversarios.minimax import minimax, construir_arbol as construir_arbol_minimax


def test_igualdad_minimax_alfa_beta():
    arbol = construir_arbol_minimax()
    valor_minimax, nodos_minimax = minimax(arbol, profundidad=3)
    arbol_beta = construir_arbol_alfa()
    valor_alfa, nodos_alfa, podados = alfa_beta(arbol_beta, profundidad=3)
    assert valor_minimax == valor_alfa
    assert nodos_alfa <= nodos_minimax
    assert podados == 2


def test_teoria_juegos_basica():
    from src.teoria_juegos.estrategias import analizar_juego_logistico, mejores_respuestas

    analisis = analizar_juego_logistico()
    assert "matriz" in analisis
    assert len(analisis["matriz"]) == 3
    assert analisis["nash"] == [(0, 0), (1, 1), (2, 2)]
    mejores = mejores_respuestas(analisis["matriz"])
    for fila, columna in analisis["nash"]:
        assert columna in mejores["filas"][fila]["columnas"]
        assert fila in mejores["columnas"][columna]["filas"]
