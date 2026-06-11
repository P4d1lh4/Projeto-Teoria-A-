"""Testes da implementação Python do A* e dos geradores de cenário.

Executar a partir da raiz do repositório:
    python -m unittest discover -s python -v
"""

import unittest

from astar import astar, manhattan
from scenarios import (
    caso_medio,
    fnv1a,
    melhor_caso,
    mulberry32,
    pior_caso,
)

# Valores de referência do mulberry32, gerados pela implementação canônica em
# JavaScript. Os MESMOS valores estão fixados em javascript/test/astar.test.js:
# se qualquer uma das portas divergir, os testes acusam.
PRNG_SEED_123 = [3381219976, 766838775, 2127363934, 993692063, 1614012641]
PRNG_SEED_GRANDE = [725983750, 2103026515, 3240384568]  # seed 4042322160 > 2^31


def bfs_custo(grid, origem, destino):
    """Referência independente: BFS devolve o custo mínimo em grades de
    custo unitário (ou None se não há caminho)."""
    linhas, colunas = len(grid), len(grid[0])
    dist = {origem: 0}
    fila = [origem]
    i = 0
    while i < len(fila):
        v = fila[i]
        i += 1
        if v == destino:
            return dist[v]
        r, c = v
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            u = (nr, nc)
            if 0 <= nr < linhas and 0 <= nc < colunas \
                    and grid[nr][nc] == 0 and u not in dist:
                dist[u] = dist[v] + 1
                fila.append(u)
    return None


def caminho_valido(grid, caminho, origem, destino):
    """O caminho começa na origem, termina no destino, só usa células livres
    e cada passo move exatamente 1 célula na vertical ou horizontal."""
    if caminho[0] != origem or caminho[-1] != destino:
        return False
    for (r1, c1), (r2, c2) in zip(caminho, caminho[1:]):
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
        if grid[r2][c2] != 0:
            return False
    return grid[origem[0]][origem[1]] == 0


class TestManhattan(unittest.TestCase):
    def test_valores(self):
        self.assertEqual(manhattan((0, 0), (0, 0)), 0)
        self.assertEqual(manhattan((0, 0), (3, 4)), 7)
        self.assertEqual(manhattan((5, 2), (1, 9)), 11)


class TestAStar(unittest.TestCase):
    def test_origem_igual_destino(self):
        grid = [[0] * 3 for _ in range(3)]
        caminho, custo, expandidos = astar(grid, (1, 1), (1, 1))
        self.assertEqual(caminho, [(1, 1)])
        self.assertEqual(custo, 0)
        self.assertEqual(expandidos, 1)

    def test_linha_reta(self):
        """Melhor caso: heurística perfeita expande somente o caminho."""
        grid, origem, destino = melhor_caso(11)
        caminho, custo, expandidos = astar(grid, origem, destino)
        self.assertEqual(custo, 10)
        self.assertEqual(len(caminho), 11)
        self.assertTrue(caminho_valido(grid, caminho, origem, destino))
        self.assertEqual(expandidos, 11)  # só as células da linha reta

    def test_grade_2x2(self):
        grid = [[0, 0], [0, 0]]
        caminho, custo, _ = astar(grid, (0, 0), (1, 1))
        self.assertEqual(custo, 2)
        self.assertTrue(caminho_valido(grid, caminho, (0, 0), (1, 1)))

    def test_desvio_de_obstaculo(self):
        grid = [
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]
        caminho, custo, _ = astar(grid, (0, 0), (0, 2))
        self.assertEqual(custo, 6)
        self.assertTrue(caminho_valido(grid, caminho, (0, 0), (0, 2)))

    def test_sem_caminho(self):
        grid = [
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 0],
        ]
        caminho, custo, expandidos = astar(grid, (0, 0), (2, 2))
        self.assertIsNone(caminho)
        self.assertEqual(custo, float("inf"))
        self.assertEqual(expandidos, 1)  # só a origem é alcançável

    def test_origem_ou_destino_bloqueado(self):
        grid = [[1, 0], [0, 0]]
        caminho, custo, expandidos = astar(grid, (0, 0), (1, 1))
        self.assertIsNone(caminho)
        self.assertEqual(expandidos, 0)
        caminho, _, _ = astar(grid, (1, 1), (0, 0))
        self.assertIsNone(caminho)

    def test_fora_da_grade(self):
        grid = [[0, 0], [0, 0]]
        with self.assertRaises(ValueError):
            astar(grid, (-1, 0), (1, 1))
        with self.assertRaises(ValueError):
            astar(grid, (0, 0), (2, 0))

    def test_otimalidade_contra_bfs(self):
        """Propriedade central: em 25 grades aleatórias o custo do A* é
        idêntico ao da BFS (referência independente de otimalidade)."""
        for seed in range(1, 26):
            grid, origem, destino, _ = caso_medio(21, seed)
            caminho, custo, _ = astar(grid, origem, destino)
            self.assertEqual(custo, bfs_custo(grid, origem, destino),
                             msg=f"custo divergente na seed {seed}")
            self.assertEqual(custo, len(caminho) - 1)
            self.assertTrue(caminho_valido(grid, caminho, origem, destino))

    def test_serpentina(self):
        """Pior caso: custo confere com a BFS e o A* expande quase todas as
        células livres (a heurística não ajuda)."""
        grid, origem, destino = pior_caso(21)
        caminho, custo, expandidos = astar(grid, origem, destino)
        self.assertEqual(custo, bfs_custo(grid, origem, destino))
        self.assertTrue(caminho_valido(grid, caminho, origem, destino))
        livres = sum(linha.count(0) for linha in grid)
        self.assertGreaterEqual(expandidos, 0.9 * livres)


class TestCenarios(unittest.TestCase):
    def test_prng_compativel_com_javascript(self):
        rand = mulberry32(123)
        valores = [round(rand() * 4294967296) for _ in range(5)]
        self.assertEqual(valores, PRNG_SEED_123)

    def test_prng_seed_grande(self):
        rand = mulberry32(4042322160)
        valores = [round(rand() * 4294967296) for _ in range(3)]
        self.assertEqual(valores, PRNG_SEED_GRANDE)

    def test_prng_intervalo(self):
        rand = mulberry32(7)
        for _ in range(1000):
            x = rand()
            self.assertTrue(0.0 <= x < 1.0)

    def test_caso_medio_deterministico(self):
        g1, *_ = caso_medio(31, 5)
        g2, *_ = caso_medio(31, 5)
        self.assertEqual(fnv1a(g1), fnv1a(g2))
        self.assertEqual(g1, g2)

    def test_caso_medio_sempre_soluvel(self):
        for seed in (1, 7, 99):
            grid, origem, destino, _ = caso_medio(31, seed)
            self.assertIsNotNone(bfs_custo(grid, origem, destino))

    def test_melhor_caso_estrutura(self):
        grid, origem, destino = melhor_caso(51)
        self.assertEqual(origem, (25, 0))
        self.assertEqual(destino, (25, 50))
        self.assertEqual(sum(sum(l) for l in grid), 0)  # grade toda livre

    def test_pior_caso_estrutura(self):
        lado = 21
        grid, origem, destino = pior_caso(lado)
        self.assertEqual(grid[origem[0]][origem[1]], 0)
        self.assertEqual(grid[destino[0]][destino[1]], 0)
        # linhas ímpares internas têm exatamente uma abertura
        for r in range(1, lado - 1, 2):
            self.assertEqual(grid[r].count(0), 1)
        # última linha é corredor livre (lado ímpar garante isso)
        self.assertEqual(sum(grid[lado - 1]), 0)

    def test_fnv1a_conhecido(self):
        # FNV-1a de [0, 1]: h = 0x811C9DC5; h ^= 0; h *= prime; h ^= 1; h *= prime
        h = 0x811C9DC5
        h = (h * 0x01000193) & 0xFFFFFFFF
        h ^= 1
        h = (h * 0x01000193) & 0xFFFFFFFF
        self.assertEqual(fnv1a([[0, 1]]), h)


if __name__ == "__main__":
    unittest.main()
