from __future__ import annotations

from math import inf


def construir_arbol():
    return {
        "valor": None,
        "maximizando": True,
        "hijos": [
            {"valor": None, "maximizando": False, "hijos": [{"valor": 5}, {"valor": 2}, {"valor": 7}]},
            {"valor": None, "maximizando": False, "hijos": [{"valor": 1}, {"valor": 3}, {"valor": 9}]},
            {"valor": None, "maximizando": False, "hijos": [{"valor": 8}, {"valor": 6}, {"valor": 4}]},
        ],
    }


def utilidad(nodo):
    if nodo.get("valor") is not None:
        return nodo["valor"]
    if nodo.get("hijos"):
        return max(utilidad(hijo) for hijo in nodo["hijos"]) if nodo.get("maximizando", True) else min(utilidad(hijo) for hijo in nodo["hijos"])
    return 0


def minimax(nodo, profundidad=3, maximizando=None, nodos_visitados=0):
    if maximizando is None:
        maximizando = nodo.get("maximizando", True)
    if profundidad == 0 or "valor" in nodo and nodo["valor"] is not None:
        return nodo.get("valor", 0), nodos_visitados + 1
    nodos_visitados += 1
    if maximizando:
        mejor = -inf
        for hijo in nodo.get("hijos", []):
            valor, nodos_visitados = minimax(hijo, profundidad - 1, False, nodos_visitados)
            mejor = max(mejor, valor)
        return mejor, nodos_visitados
    mejor = inf
    for hijo in nodo.get("hijos", []):
        valor, nodos_visitados = minimax(hijo, profundidad - 1, True, nodos_visitados)
        mejor = min(mejor, valor)
    return mejor, nodos_visitados


def evaluar_minimax(profundidad=3):
    arbol = construir_arbol()
    valor, nodos = minimax(arbol, profundidad=profundidad)
    return {
        "valor": valor,
        "nodos_visitados": nodos,
        "profundidad": profundidad,
        "tipo_arbol": "ejemplo",
        "arbol": arbol,
    }
