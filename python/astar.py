"""Algoritmo A* (A-estrela) para caminho mínimo em grades 2D.

Problema resolvido: encontrar o caminho de menor custo entre dois pontos de uma
grade com obstáculos, movendo-se em 4 direções (cima, baixo, esquerda, direita)
com custo unitário por passo.

O A* é uma busca de melhor-primeiro que ordena a fronteira pela função
f(v) = g(v) + h(v), onde g(v) é o custo real acumulado da origem até v e h(v)
é uma estimativa heurística do custo de v até o destino. Com heurística
admissível (nunca superestima) e consistente (h(u) <= custo(u,v) + h(v)),
o A* é ótimo: o primeiro caminho encontrado é o de menor custo.

Heurística usada: distância de Manhattan — admissível e consistente para
movimento em 4 direções com custo unitário.

Pseudocódigo:
    A*(grade, origem, destino):
        aberta <- heap-mínimo ordenado por (f, h, ordem de inserção)
        g[origem] <- 0
        insere origem na aberta com f = h(origem)
        enquanto aberta não vazia:
            v <- remove-mínimo(aberta)
            se v já foi expandido: continua          # entrada obsoleta no heap
            marca v como expandido
            se v == destino: retorna caminho reconstruído
            para cada vizinho u de v (4 direções, livre e dentro da grade):
                g' <- g[v] + 1
                se g' < g[u]:
                    g[u] <- g'; pai[u] <- v
                    insere u na aberta com f = g' + h(u)
        retorna "sem caminho"

Complexidade (V células livres, E arestas; em grades E <= 4V, logo E = O(V)):
    - Pior caso:   O(V log V) tempo (cada aresta pode gerar uma inserção no
                   heap de tamanho O(V)), O(V) memória.
    - Melhor caso: Omega(L) expansões, onde L é o comprimento do caminho ótimo
                   (heurística perfeita guia direto ao destino).
"""

from __future__ import annotations

import heapq
from itertools import count

# Ordem fixa de exploração dos vizinhos: cima, baixo, esquerda, direita.
# A MESMA ordem é usada na implementação JavaScript para que as duas
# implementações expandam exatamente os mesmos nós, na mesma ordem.
DIRECOES = ((-1, 0), (1, 0), (0, -1), (0, 1))

LIVRE = 0
OBSTACULO = 1


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Distância de Manhattan entre duas células (linha, coluna)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: list[list[int]],
          start: tuple[int, int],
          goal: tuple[int, int]):
    """Executa o A* na grade.

    Args:
        grid: matriz de inteiros (0 = livre, 1 = obstáculo).
        start: célula de origem (linha, coluna).
        goal: célula de destino (linha, coluna).

    Returns:
        (caminho, custo, expandidos):
        - caminho: lista de células da origem ao destino, ou None se não existe.
        - custo: número de passos do caminho (inf se não existe).
        - expandidos: quantidade de nós retirados do heap e processados
          (métrica de trabalho do algoritmo, idêntica entre as linguagens).
    """
    linhas, colunas = len(grid), len(grid[0])

    for nome, (r, c) in (("origem", start), ("destino", goal)):
        if not (0 <= r < linhas and 0 <= c < colunas):
            raise ValueError(f"{nome} {(r, c)} fora da grade {linhas}x{colunas}")

    if grid[start[0]][start[1]] == OBSTACULO or grid[goal[0]][goal[1]] == OBSTACULO:
        return None, float("inf"), 0

    # Desempate do heap: menor f, depois menor h (favorece nós mais próximos
    # do destino), depois ordem de inserção (determinismo total — essencial
    # para a comparação justa entre Python e JavaScript).
    ordem = count()
    h0 = manhattan(start, goal)
    aberta: list[tuple[int, int, int, tuple[int, int]]] = [(h0, h0, next(ordem), start)]
    g_score: dict[tuple[int, int], int] = {start: 0}
    pai: dict[tuple[int, int], tuple[int, int]] = {}
    expandido: set[tuple[int, int]] = set()
    expandidos = 0

    while aberta:
        _f, _h, _, v = heapq.heappop(aberta)
        if v in expandido:
            continue  # entrada obsoleta (o nó já saiu com g menor)
        expandido.add(v)
        expandidos += 1

        if v == goal:
            return _reconstruir(pai, v), g_score[v], expandidos

        gv = g_score[v]
        r, c = v
        for dr, dc in DIRECOES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < linhas and 0 <= nc < colunas and grid[nr][nc] == LIVRE:
                u = (nr, nc)
                if u in expandido:
                    continue
                novo_g = gv + 1
                if novo_g < g_score.get(u, float("inf")):
                    g_score[u] = novo_g
                    pai[u] = v
                    hu = manhattan(u, goal)
                    heapq.heappush(aberta, (novo_g + hu, hu, next(ordem), u))

    return None, float("inf"), expandidos


def _reconstruir(pai: dict, v: tuple[int, int]) -> list[tuple[int, int]]:
    """Reconstrói o caminho do destino até a origem seguindo os pais."""
    caminho = [v]
    while v in pai:
        v = pai[v]
        caminho.append(v)
    caminho.reverse()
    return caminho
