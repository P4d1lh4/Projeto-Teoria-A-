/**
 * Testes da implementação JavaScript do A* e dos geradores de cenário.
 *
 * Executar a partir da raiz do repositório:
 *     node --test javascript/test/astar.test.js
 * (ou `npm test` de dentro de javascript/)
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import { astar, manhattan, MinHeap } from "../astar.js";
import {
  casoMedio,
  fnv1a,
  melhorCaso,
  mulberry32,
  piorCaso,
} from "../scenarios.js";

// Mesmos valores de referência fixados em python/test_astar.py — se qualquer
// uma das implementações do PRNG divergir, os testes acusam.
const PRNG_SEED_123 = [3381219976, 766838775, 2127363934, 993692063, 1614012641];
const PRNG_SEED_GRANDE = [725983750, 2103026515, 3240384568]; // seed 4042322160 > 2^31

/** Referência independente: BFS devolve o custo mínimo (ou null). */
function bfsCusto(grid, origem, destino) {
  const linhas = grid.length;
  const colunas = grid[0].length;
  const dist = new Int32Array(linhas * colunas).fill(-1);
  dist[origem[0] * colunas + origem[1]] = 0;
  const fila = [origem];
  let i = 0;
  while (i < fila.length) {
    const [r, c] = fila[i];
    i++;
    if (r === destino[0] && c === destino[1]) return dist[r * colunas + c];
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < linhas && nc >= 0 && nc < colunas
          && grid[nr][nc] === 0 && dist[nr * colunas + nc] === -1) {
        dist[nr * colunas + nc] = dist[r * colunas + c] + 1;
        fila.push([nr, nc]);
      }
    }
  }
  return null;
}

function caminhoValido(grid, caminho, origem, destino) {
  if (caminho[0][0] !== origem[0] || caminho[0][1] !== origem[1]) return false;
  const fim = caminho[caminho.length - 1];
  if (fim[0] !== destino[0] || fim[1] !== destino[1]) return false;
  for (let i = 1; i < caminho.length; i++) {
    const [r1, c1] = caminho[i - 1];
    const [r2, c2] = caminho[i];
    if (Math.abs(r1 - r2) + Math.abs(c1 - c2) !== 1) return false;
    if (grid[r2][c2] !== 0) return false;
  }
  return grid[origem[0]][origem[1]] === 0;
}

test("manhattan: valores conhecidos", () => {
  assert.equal(manhattan([0, 0], [0, 0]), 0);
  assert.equal(manhattan([0, 0], [3, 4]), 7);
  assert.equal(manhattan([5, 2], [1, 9]), 11);
});

test("MinHeap: extrai em ordem (f, h, ordem) — estresse com PRNG", () => {
  const rand = mulberry32(99);
  const itens = [];
  for (let i = 0; i < 2000; i++) {
    itens.push([Math.floor(rand() * 50), Math.floor(rand() * 50), i, i]);
  }
  const heap = new MinHeap();
  for (const item of itens) heap.push(item);

  const esperado = [...itens].sort((a, b) =>
    a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);
  const obtido = [];
  while (heap.tamanho > 0) obtido.push(heap.pop());
  assert.deepEqual(obtido, esperado);
});

test("origem igual ao destino", () => {
  const grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  const { caminho, custo, expandidos } = astar(grid, [1, 1], [1, 1]);
  assert.deepEqual(caminho, [[1, 1]]);
  assert.equal(custo, 0);
  assert.equal(expandidos, 1);
});

test("melhor caso: heurística perfeita expande somente o caminho", () => {
  const { grid, origem, destino } = melhorCaso(11);
  const { caminho, custo, expandidos } = astar(grid, origem, destino);
  assert.equal(custo, 10);
  assert.equal(caminho.length, 11);
  assert.ok(caminhoValido(grid, caminho, origem, destino));
  assert.equal(expandidos, 11);
});

test("desvio de obstáculo", () => {
  const grid = [
    [0, 1, 0],
    [0, 1, 0],
    [0, 0, 0],
  ];
  const { caminho, custo } = astar(grid, [0, 0], [0, 2]);
  assert.equal(custo, 6);
  assert.ok(caminhoValido(grid, caminho, [0, 0], [0, 2]));
});

test("sem caminho", () => {
  const grid = [
    [0, 1, 0],
    [1, 1, 0],
    [0, 0, 0],
  ];
  const { caminho, custo, expandidos } = astar(grid, [0, 0], [2, 2]);
  assert.equal(caminho, null);
  assert.equal(custo, Infinity);
  assert.equal(expandidos, 1); // só a origem é alcançável
});

test("origem ou destino bloqueado", () => {
  const grid = [[1, 0], [0, 0]];
  assert.equal(astar(grid, [0, 0], [1, 1]).caminho, null);
  assert.equal(astar(grid, [1, 1], [0, 0]).caminho, null);
});

test("origem ou destino fora da grade", () => {
  const grid = [[0, 0], [0, 0]];
  assert.throws(() => astar(grid, [-1, 0], [1, 1]), RangeError);
  assert.throws(() => astar(grid, [0, 0], [2, 0]), RangeError);
});

test("otimalidade contra BFS em 25 grades aleatórias", () => {
  for (let seed = 1; seed <= 25; seed++) {
    const { grid, origem, destino } = casoMedio(21, seed);
    const { caminho, custo } = astar(grid, origem, destino);
    assert.equal(custo, bfsCusto(grid, origem, destino),
      `custo divergente na seed ${seed}`);
    assert.equal(custo, caminho.length - 1);
    assert.ok(caminhoValido(grid, caminho, origem, destino));
  }
});

test("pior caso (serpentina): ótimo e expande quase tudo", () => {
  const { grid, origem, destino } = piorCaso(21);
  const { caminho, custo, expandidos } = astar(grid, origem, destino);
  assert.equal(custo, bfsCusto(grid, origem, destino));
  assert.ok(caminhoValido(grid, caminho, origem, destino));
  let livres = 0;
  for (const linha of grid) for (const c of linha) if (c === 0) livres++;
  assert.ok(expandidos >= 0.9 * livres);
});

test("PRNG compatível com a referência fixada (seed 123)", () => {
  const rand = mulberry32(123);
  const valores = [];
  for (let i = 0; i < 5; i++) valores.push(Math.round(rand() * 4294967296));
  assert.deepEqual(valores, PRNG_SEED_123);
});

test("PRNG com seed acima de 2^31", () => {
  const rand = mulberry32(4042322160);
  const valores = [];
  for (let i = 0; i < 3; i++) valores.push(Math.round(rand() * 4294967296));
  assert.deepEqual(valores, PRNG_SEED_GRANDE);
});

test("caso médio é determinístico para a mesma seed", () => {
  const a = casoMedio(31, 5);
  const b = casoMedio(31, 5);
  assert.equal(fnv1a(a.grid), fnv1a(b.grid));
  assert.deepEqual(a.grid, b.grid);
});

test("caso médio sempre solúvel", () => {
  for (const seed of [1, 7, 99]) {
    const { grid, origem, destino } = casoMedio(31, seed);
    assert.notEqual(bfsCusto(grid, origem, destino), null);
  }
});

test("estrutura do pior caso (serpentina)", () => {
  const lado = 21;
  const { grid, origem, destino } = piorCaso(lado);
  assert.equal(grid[origem[0]][origem[1]], 0);
  assert.equal(grid[destino[0]][destino[1]], 0);
  for (let r = 1; r < lado - 1; r += 2) {
    assert.equal(grid[r].filter((c) => c === 0).length, 1);
  }
  assert.equal(grid[lado - 1].reduce((s, c) => s + c, 0), 0);
});

test("FNV-1a: valor conhecido", () => {
  let h = 0x811C9DC5;
  h = Math.imul(h, 0x01000193) >>> 0;
  h ^= 1;
  h = Math.imul(h, 0x01000193) >>> 0;
  assert.equal(fnv1a([[0, 1]]), h);
});
