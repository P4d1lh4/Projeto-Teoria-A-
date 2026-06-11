/**
 * Protocolo experimental do A* em JavaScript — espelho de python/benchmark.py.
 *
 * - 3 cenários (melhor, médio, pior) × tamanhos pequena/média/grande
 *   (+ intermediários), 30 rodadas medidas após 3 de aquecimento (importante
 *   no Node para estabilizar o JIT do V8);
 * - medição com process.hrtime.bigint() (nanossegundos), cronometrando
 *   APENAS a chamada do algoritmo;
 * - caso médio: sementes 1..30, as mesmas do Python (PRNG compartilhado),
 *   logo grades idênticas nas duas linguagens.
 *
 * Saída: results/resultados_javascript.csv
 *
 * Uso:
 *     node javascript/benchmark.js [--rapido]
 */

import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { astar } from "./astar.js";
import { TAMANHOS, casoMedio, melhorCaso, piorCaso } from "./scenarios.js";

const LINGUAGEM = "javascript";
const RODADAS = 30;
const AQUECIMENTO = 3;
const SEEDS_AQUECIMENTO = [9001, 9002, 9003];

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), "..");
const ARQUIVO_SAIDA = join(RAIZ, "results", `resultados_${LINGUAGEM}.csv`);

const CABECALHO = [
  "linguagem", "cenario", "rotulo", "lado", "n_celulas",
  "rodada", "seed", "tempo_ms", "nos_expandidos", "custo_caminho",
];

/** Cronometra uma execução do A*. */
function cronometrar(grid, origem, destino) {
  const inicio = process.hrtime.bigint();
  const { custo, expandidos } = astar(grid, origem, destino);
  const fim = process.hrtime.bigint();
  return { tempoMs: Number(fim - inicio) / 1e6, expandidos, custo };
}

function executar(rodadas, tamanhos) {
  const linhasCsv = [];

  for (const cenario of ["melhor", "medio", "pior"]) {
    for (const [lado, rotulo] of tamanhos) {
      const nCelulas = lado * lado;

      if (cenario === "medio") {
        for (const seed of SEEDS_AQUECIMENTO.slice(0, AQUECIMENTO)) {
          const { grid, origem, destino } = casoMedio(lado, seed);
          cronometrar(grid, origem, destino);
        }
        for (let rodada = 1; rodada <= rodadas; rodada++) {
          const { grid, origem, destino, seedEfetiva } = casoMedio(lado, rodada);
          const { tempoMs, expandidos, custo } = cronometrar(grid, origem, destino);
          linhasCsv.push([
            LINGUAGEM, cenario, rotulo, lado, nCelulas,
            rodada, seedEfetiva, tempoMs.toFixed(6), expandidos, custo,
          ]);
        }
      } else {
        const gerador = cenario === "melhor" ? melhorCaso : piorCaso;
        const { grid, origem, destino } = gerador(lado);
        for (let i = 0; i < AQUECIMENTO; i++) cronometrar(grid, origem, destino);
        for (let rodada = 1; rodada <= rodadas; rodada++) {
          const { tempoMs, expandidos, custo } = cronometrar(grid, origem, destino);
          linhasCsv.push([
            LINGUAGEM, cenario, rotulo, lado, nCelulas,
            rodada, "", tempoMs.toFixed(6), expandidos, custo,
          ]);
        }
      }

      console.error(`[${LINGUAGEM}] ${cenario.padEnd(6)} lado=${String(lado).padEnd(4)} (${rotulo}) ok`);
    }
  }

  return linhasCsv;
}

function main() {
  const rapido = process.argv.includes("--rapido");
  const rodadas = rapido ? 5 : RODADAS;
  const tamanhos = rapido ? TAMANHOS.filter(([, r]) => r !== "intermediaria") : TAMANHOS;

  const linhasCsv = executar(rodadas, tamanhos);

  mkdirSync(join(RAIZ, "results"), { recursive: true });
  const conteudo = [CABECALHO.join(","), ...linhasCsv.map((l) => l.join(","))].join("\n") + "\n";
  writeFileSync(ARQUIVO_SAIDA, conteudo, "utf-8");

  console.error(`${linhasCsv.length} medições gravadas em ${ARQUIVO_SAIDA}`);
}

main();
