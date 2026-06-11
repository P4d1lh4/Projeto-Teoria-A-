/**
 * Geradores de cenário para os experimentos com o A* — espelho exato de
 * python/scenarios.py.
 *
 * O PRNG (mulberry32) e o hash (FNV-1a) são bit a bit idênticos nas duas
 * linguagens: as grades geradas, os custos e os nós expandidos são os mesmos,
 * de modo que a única variável dos experimentos é a linguagem/runtime.
 *
 * Modo de verificação (usado por tools/verificar_equivalencia.py):
 *     node javascript/scenarios.js --check
 * imprime exatamente a mesma saída de `python python/scenarios.py --check`.
 */

import { astar } from "./astar.js";

export const LIVRE = 0;
export const OBSTACULO = 1;

// (lado, rótulo) — mesmos tamanhos do Python.
export const TAMANHOS = [
  [51, "pequena"],
  [101, "intermediaria"],
  [151, "media"],
  [201, "intermediaria"],
  [251, "intermediaria"],
  [301, "grande"],
];

export const DENSIDADE_OBSTACULOS = 0.25;

/** PRNG mulberry32 (implementação canônica). Floats uniformes em [0, 1). */
export function mulberry32(seed) {
  let estado = seed >>> 0;
  return function rand() {
    estado = (estado + 0x6D2B79F5) >>> 0;
    let t = estado;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Hash FNV-1a 32 bits do conteúdo da grade (mesma fórmula no Python). */
export function fnv1a(grid) {
  let h = 0x811C9DC5;
  for (const linha of grid) {
    for (const celula of linha) {
      h ^= celula;
      h = Math.imul(h, 0x01000193) >>> 0;
    }
  }
  return h >>> 0;
}

function gradeVazia(lado) {
  return Array.from({ length: lado }, () => new Array(lado).fill(LIVRE));
}

/** Melhor caso: grade vazia; origem e destino nas pontas da linha central. */
export function melhorCaso(lado) {
  const grid = gradeVazia(lado);
  const meio = Math.floor(lado / 2);
  return { grid, origem: [meio, 0], destino: [meio, lado - 1] };
}

/** Pior caso: labirinto em serpentina (aberturas alternando direita/esquerda). */
export function piorCaso(lado) {
  const grid = gradeVazia(lado);
  for (let r = 1; r < lado - 1; r += 2) {
    const abertura = (Math.floor(r / 2) % 2 === 0) ? lado - 1 : 0;
    for (let c = 0; c < lado; c++) {
      if (c !== abertura) grid[r][c] = OBSTACULO;
    }
  }
  return { grid, origem: [0, 0], destino: [lado - 1, lado - 1] };
}

/**
 * Caso médio: obstáculos aleatórios (densidade 25%) entre cantos opostos.
 * Se a grade sorteada não tiver caminho, deriva a próxima semente com a
 * MESMA regra do Python — as duas linguagens convergem para a mesma grade.
 */
export function casoMedio(lado, seed) {
  const origem = [0, 0];
  const destino = [lado - 1, lado - 1];
  for (let tentativa = 0; ; tentativa++) {
    const seedEfetiva = (seed + tentativa * 1000003) >>> 0;
    const rand = mulberry32(seedEfetiva);
    const grid = [];
    for (let r = 0; r < lado; r++) {
      const linha = new Array(lado);
      for (let c = 0; c < lado; c++) {
        linha[c] = rand() < DENSIDADE_OBSTACULOS ? OBSTACULO : LIVRE;
      }
      grid.push(linha);
    }
    grid[origem[0]][origem[1]] = LIVRE;
    grid[destino[0]][destino[1]] = LIVRE;
    if (temCaminho(grid, origem, destino)) {
      return { grid, origem, destino, seedEfetiva };
    }
  }
}

/** BFS booleana usada apenas na geração (fora da medição de tempo). */
export function temCaminho(grid, origem, destino) {
  const linhas = grid.length;
  const colunas = grid[0].length;
  const visitado = new Uint8Array(linhas * colunas);
  visitado[origem[0] * colunas + origem[1]] = 1;
  const fila = [origem];
  let i = 0;
  while (i < fila.length) {
    const [r, c] = fila[i];
    i++;
    if (r === destino[0] && c === destino[1]) return true;
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < linhas && nc >= 0 && nc < colunas
          && !visitado[nr * colunas + nc] && grid[nr][nc] === LIVRE) {
        visitado[nr * colunas + nc] = 1;
        fila.push([nr, nc]);
      }
    }
  }
  return false;
}

/** Saída idêntica à de `python python/scenarios.py --check`. */
function modoVerificacao() {
  const linhasSaida = [];
  const lados = [21, 51];

  const rand = mulberry32(123);
  const valores = [];
  for (let i = 0; i < 5; i++) valores.push(Math.round(rand() * 4294967296));
  linhasSaida.push(`prng123 ${valores.join(" ")}`);

  for (const lado of lados) {
    for (const [nome, dados] of [["melhor", melhorCaso(lado)], ["pior", piorCaso(lado)]]) {
      const { grid, origem, destino } = dados;
      const { custo, expandidos } = astar(grid, origem, destino);
      linhasSaida.push(`${nome},${lado},${fnv1a(grid)},${custo},${expandidos}`);
    }
    for (const seed of [1, 2, 3]) {
      const { grid, origem, destino, seedEfetiva } = casoMedio(lado, seed);
      const { custo, expandidos } = astar(grid, origem, destino);
      linhasSaida.push(`medio,${lado},${seedEfetiva},${fnv1a(grid)},${custo},${expandidos}`);
    }
  }
  console.log(linhasSaida.join("\n"));
}

if (process.argv.includes("--check")) {
  modoVerificacao();
}
