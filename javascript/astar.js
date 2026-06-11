/**
 * Algoritmo A* (A-estrela) para caminho mínimo em grades 2D.
 *
 * Espelho exato da implementação Python (python/astar.py): mesma ordem de
 * exploração de vizinhos, mesmo critério de desempate no heap
 * (f, depois h, depois ordem de inserção) e, portanto, exatamente os mesmos
 * nós expandidos — o que torna a comparação de tempos entre as duas
 * linguagens uma comparação justa do MESMO trabalho algorítmico.
 *
 * Movimento em 4 direções com custo unitário; heurística de Manhattan
 * (admissível e consistente), o que garante a otimalidade do caminho.
 */

// Ordem fixa: cima, baixo, esquerda, direita (idêntica ao Python).
export const DIRECOES = [[-1, 0], [1, 0], [0, -1], [0, 1]];

export const LIVRE = 0;
export const OBSTACULO = 1;

/** Distância de Manhattan entre duas células [linha, coluna]. */
export function manhattan(a, b) {
  return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
}

/**
 * Heap binário de mínimo com desempate lexicográfico (f, h, ordem).
 * Cada elemento é [f, h, ordem, indiceDaCelula].
 */
export class MinHeap {
  constructor() {
    this.itens = [];
  }

  get tamanho() {
    return this.itens.length;
  }

  static _menor(a, b) {
    if (a[0] !== b[0]) return a[0] < b[0];
    if (a[1] !== b[1]) return a[1] < b[1];
    return a[2] < b[2];
  }

  push(item) {
    const itens = this.itens;
    itens.push(item);
    let i = itens.length - 1;
    while (i > 0) {
      const paiIdx = (i - 1) >> 1;
      if (MinHeap._menor(itens[i], itens[paiIdx])) {
        [itens[i], itens[paiIdx]] = [itens[paiIdx], itens[i]];
        i = paiIdx;
      } else {
        break;
      }
    }
  }

  pop() {
    const itens = this.itens;
    const topo = itens[0];
    const ultimo = itens.pop();
    if (itens.length > 0) {
      itens[0] = ultimo;
      let i = 0;
      for (;;) {
        const esq = 2 * i + 1;
        const dir = 2 * i + 2;
        let menor = i;
        if (esq < itens.length && MinHeap._menor(itens[esq], itens[menor])) menor = esq;
        if (dir < itens.length && MinHeap._menor(itens[dir], itens[menor])) menor = dir;
        if (menor === i) break;
        [itens[i], itens[menor]] = [itens[menor], itens[i]];
        i = menor;
      }
    }
    return topo;
  }
}

/**
 * Executa o A* na grade.
 *
 * @param {number[][]} grid  matriz (0 = livre, 1 = obstáculo)
 * @param {[number, number]} start  célula de origem [linha, coluna]
 * @param {[number, number]} goal   célula de destino [linha, coluna]
 * @returns {{caminho: Array<[number,number]>|null, custo: number, expandidos: number}}
 *   caminho da origem ao destino (null se não existe), custo em passos
 *   (Infinity se não existe) e número de nós expandidos.
 */
export function astar(grid, start, goal) {
  const linhas = grid.length;
  const colunas = grid[0].length;

  for (const [nome, [r, c]] of [["origem", start], ["destino", goal]]) {
    if (!(r >= 0 && r < linhas && c >= 0 && c < colunas)) {
      throw new RangeError(`${nome} (${r}, ${c}) fora da grade ${linhas}x${colunas}`);
    }
  }

  if (grid[start[0]][start[1]] === OBSTACULO || grid[goal[0]][goal[1]] === OBSTACULO) {
    return { caminho: null, custo: Infinity, expandidos: 0 };
  }

  // Células indexadas por r * colunas + c. Map/Set espelham os dicionários
  // da versão Python: a memória cresce só com a região explorada, mantendo a
  // mesma assintótica nas duas implementações (sem inicialização Theta(n)).
  const idxOrigem = start[0] * colunas + start[1];
  const idxDestino = goal[0] * colunas + goal[1];

  const gScore = new Map([[idxOrigem, 0]]);
  const pai = new Map();
  const expandido = new Set();

  const heap = new MinHeap();
  let ordem = 0;
  const h0 = manhattan(start, goal);
  heap.push([h0, h0, ordem++, idxOrigem]);

  let expandidos = 0;

  while (heap.tamanho > 0) {
    const [, , , v] = heap.pop();
    if (expandido.has(v)) continue; // entrada obsoleta no heap
    expandido.add(v);
    expandidos++;

    if (v === idxDestino) {
      return { caminho: reconstruir(pai, v, colunas), custo: gScore.get(v), expandidos };
    }

    const r = Math.floor(v / colunas);
    const c = v % colunas;
    const gv = gScore.get(v);

    for (const [dr, dc] of DIRECOES) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < linhas && nc >= 0 && nc < colunas && grid[nr][nc] === LIVRE) {
        const u = nr * colunas + nc;
        if (expandido.has(u)) continue;
        const novoG = gv + 1;
        const gAtual = gScore.get(u);
        if (gAtual === undefined || novoG < gAtual) {
          gScore.set(u, novoG);
          pai.set(u, v);
          const hu = Math.abs(nr - goal[0]) + Math.abs(nc - goal[1]);
          heap.push([novoG + hu, hu, ordem++, u]);
        }
      }
    }
  }

  return { caminho: null, custo: Infinity, expandidos };
}

/** Reconstrói o caminho seguindo os pais, do destino para a origem. */
function reconstruir(pai, v, colunas) {
  const caminho = [];
  while (v !== undefined) {
    caminho.push([Math.floor(v / colunas), v % colunas]);
    v = pai.get(v);
  }
  caminho.reverse();
  return caminho;
}
