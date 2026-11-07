from __future__ import annotations

from math import inf


def _contar_nodos(nodo, profundidad):
    if profundidad == 0 or ("valor" in nodo and nodo["valor"] is not None):
        return 1
    return 1 + sum(_contar_nodos(hijo, profundidad - 1) for hijo in nodo.get("hijos", []))


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


def alfa_beta(nodo, profundidad=3, alpha=-inf, beta=inf, maximizando=None, nodos_visitados=0, nodos_podados=0):
    if maximizando is None:
        maximizando = nodo.get("maximizando", True)
    if profundidad == 0 or ("valor" in nodo and nodo["valor"] is not None):
        return nodo.get("valor", 0), nodos_visitados + 1, nodos_podados
    nodos_visitados += 1
    if maximizando:
        mejor = -inf
        hijos = nodo.get("hijos", [])
        for indice, hijo in enumerate(hijos):
            valor, nodos_visitados, nodos_podados = alfa_beta(hijo, profundidad - 1, alpha, beta, False, nodos_visitados, nodos_podados)
            mejor = max(mejor, valor)
            alpha = max(alpha, mejor)
            if beta <= alpha:
                nodos_podados += sum(_contar_nodos(restante, profundidad - 1) for restante in hijos[indice + 1:])
                break
        return mejor, nodos_visitados, nodos_podados
    mejor = inf
    hijos = nodo.get("hijos", [])
    for indice, hijo in enumerate(hijos):
        valor, nodos_visitados, nodos_podados = alfa_beta(hijo, profundidad - 1, alpha, beta, True, nodos_visitados, nodos_podados)
        mejor = min(mejor, valor)
        beta = min(beta, mejor)
        if beta <= alpha:
            nodos_podados += sum(_contar_nodos(restante, profundidad - 1) for restante in hijos[indice + 1:])
            break
    return mejor, nodos_visitados, nodos_podados


def evaluar_alfa_beta(profundidad=3):
    arbol = construir_arbol()
    valor, nodos, podados = alfa_beta(arbol, profundidad=profundidad)
    return {
        "valor": valor,
        "nodos_visitados": nodos,
        "nodos_podados": podados,
        "profundidad": profundidad,
        "tipo_arbol": "ejemplo",
        "arbol": arbol,
    }
