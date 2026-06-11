"""Geradores de cenário para os experimentos com o A*.

Os três cenários exigidos pelo protocolo experimental:

- Melhor caso:  grade vazia com origem e destino na mesma linha. A heurística
                de Manhattan é perfeita nesse trajeto e o A* expande apenas as
                células do caminho reto.
- Caso médio:   obstáculos aleatórios (densidade 25%) com origem e destino em
                cantos opostos. Cada rodada usa uma semente diferente.
- Pior caso:    labirinto em serpentina — paredes horizontais alternadas que
                forçam o caminho a zigue-zaguear pela grade inteira. A
                heurística aponta "para baixo" enquanto o caminho precisa ir
                e voltar: o A* expande praticamente todas as células livres.

O gerador pseudoaleatório (mulberry32) e a função de hash (FNV-1a) são
implementados de forma BIT A BIT idêntica em python/scenarios.py e
javascript/scenarios.js, garantindo que as duas linguagens processem
exatamente as mesmas grades — requisito de comparabilidade do experimento.

Os lados das grades são ímpares (51, 151, 301...) para que a última linha do
labirinto em serpentina seja sempre um corredor livre.
"""

from __future__ import annotations

LIVRE = 0
OBSTACULO = 1

# (lado, rótulo) — pequena/média/grande são os tamanhos nomeados do protocolo;
# os intermediários dão resolução às curvas dos gráficos.
TAMANHOS = [
    (51, "pequena"),
    (101, "intermediaria"),
    (151, "media"),
    (201, "intermediaria"),
    (251, "intermediaria"),
    (301, "grande"),
]

DENSIDADE_OBSTACULOS = 0.25  # caso médio


def mulberry32(seed: int):
    """PRNG mulberry32 — réplica exata da versão JavaScript.

    Toda a aritmética é feita módulo 2^32 (máscara 0xFFFFFFFF) para reproduzir
    o comportamento dos operadores de 32 bits do JavaScript (Math.imul, >>>, ^).
    Retorna uma função que produz floats uniformes em [0, 1).
    """
    estado = seed & 0xFFFFFFFF

    def rand() -> float:
        nonlocal estado
        estado = (estado + 0x6D2B79F5) & 0xFFFFFFFF
        t = estado
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t ^ ((t + ((t ^ (t >> 7)) * (t | 61))) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rand


def fnv1a(grid: list[list[int]]) -> int:
    """Hash FNV-1a 32 bits do conteúdo da grade (mesma fórmula no JS)."""
    h = 0x811C9DC5
    for linha in grid:
        for celula in linha:
            h ^= celula
            h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def melhor_caso(lado: int):
    """Grade vazia; origem e destino nas pontas da linha central."""
    grid = [[LIVRE] * lado for _ in range(lado)]
    meio = lado // 2
    return grid, (meio, 0), (meio, lado - 1)


def pior_caso(lado: int):
    """Labirinto em serpentina: paredes nas linhas ímpares com uma única
    abertura, alternando entre a direita e a esquerda."""
    grid = [[LIVRE] * lado for _ in range(lado)]
    for r in range(1, lado - 1, 2):
        abertura = lado - 1 if ((r // 2) % 2 == 0) else 0
        for c in range(lado):
            if c != abertura:
                grid[r][c] = OBSTACULO
    return grid, (0, 0), (lado - 1, lado - 1)


def caso_medio(lado: int, seed: int):
    """Grade com obstáculos aleatórios (densidade 25%).

    Se a grade sorteada não tiver caminho entre os cantos, tenta a próxima
    semente derivada (mesma regra nas duas linguagens, logo mesma grade final).
    Retorna também a semente efetivamente usada, para registro no CSV.
    """
    origem, destino = (0, 0), (lado - 1, lado - 1)
    tentativa = 0
    while True:
        seed_efetiva = (seed + tentativa * 1000003) & 0xFFFFFFFF
        rand = mulberry32(seed_efetiva)
        grid = []
        for _r in range(lado):
            linha = []
            for _c in range(lado):
                linha.append(OBSTACULO if rand() < DENSIDADE_OBSTACULOS else LIVRE)
            grid.append(linha)
        grid[origem[0]][origem[1]] = LIVRE
        grid[destino[0]][destino[1]] = LIVRE
        if _tem_caminho(grid, origem, destino):
            return grid, origem, destino, seed_efetiva
        tentativa += 1


def _tem_caminho(grid, origem, destino) -> bool:
    """BFS booleana usada apenas na geração (fora da medição de tempo)."""
    linhas, colunas = len(grid), len(grid[0])
    visitado = [[False] * colunas for _ in range(linhas)]
    visitado[origem[0]][origem[1]] = True
    fila = [origem]
    i = 0
    while i < len(fila):
        r, c = fila[i]
        i += 1
        if (r, c) == destino:
            return True
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < linhas and 0 <= nc < colunas \
                    and not visitado[nr][nc] and grid[nr][nc] == LIVRE:
                visitado[nr][nc] = True
                fila.append((nr, nc))
    return False


def _modo_verificacao():
    """Imprime uma linha por cenário com hash da grade, custo e nós expandidos.

    Usado por tools/verificar_equivalencia.py: a saída deste módulo e a de
    `node javascript/scenarios.js --check` devem ser IDÊNTICAS.
    """
    from astar import astar

    lados = [21, 51]
    # Valores do PRNG impressos como inteiros (k = x * 2^32, exato em float64)
    # para comparação bit a bit com o JavaScript, sem ruído de formatação.
    rand = mulberry32(123)
    print("prng123", " ".join(str(round(rand() * 4294967296)) for _ in range(5)))
    for lado in lados:
        for nome, dados in (
            ("melhor", melhor_caso(lado)),
            ("pior", pior_caso(lado)),
        ):
            grid, origem, destino = dados
            _, custo, expandidos = astar(grid, origem, destino)
            print(f"{nome},{lado},{fnv1a(grid)},{custo},{expandidos}")
        for seed in (1, 2, 3):
            grid, origem, destino, seed_usada = caso_medio(lado, seed)
            _, custo, expandidos = astar(grid, origem, destino)
            print(f"medio,{lado},{seed_usada},{fnv1a(grid)},{custo},{expandidos}")


if __name__ == "__main__":
    import sys

    if "--check" in sys.argv:
        _modo_verificacao()
    else:
        print(__doc__)
