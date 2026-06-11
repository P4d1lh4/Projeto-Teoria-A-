"""Protocolo experimental do A* em Python.

Segue a metodologia da especificação do projeto:
- 3 cenários (melhor caso, caso médio, pior caso);
- tamanhos de entrada pequena/média/grande (+ intermediários para as curvas);
- 30 rodadas medidas por (cenário, tamanho), após 3 rodadas de aquecimento
  descartadas (estabiliza caches e, no caso do Node, o JIT — o mesmo
  protocolo é usado nas duas linguagens);
- medição com time.perf_counter_ns() (alta precisão), cronometrando APENAS a
  chamada do algoritmo (a geração da grade fica fora da medição);
- caso médio: cada rodada usa uma grade aleatória diferente (sementes 1..30,
  as MESMAS nas duas linguagens, graças ao PRNG compartilhado).

Saída: results/resultados_python.csv

Uso:
    python python/benchmark.py [--rapido]

    --rapido: 5 rodadas e só os tamanhos nomeados (para teste do script).
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

from astar import astar
from scenarios import TAMANHOS, caso_medio, melhor_caso, pior_caso

LINGUAGEM = "python"
RODADAS = 30
AQUECIMENTO = 3
SEEDS_AQUECIMENTO = (9001, 9002, 9003)

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_SAIDA = RAIZ / "results" / f"resultados_{LINGUAGEM}.csv"

CABECALHO = [
    "linguagem", "cenario", "rotulo", "lado", "n_celulas",
    "rodada", "seed", "tempo_ms", "nos_expandidos", "custo_caminho",
]


def cronometrar(grid, origem, destino):
    """Cronometra uma execução do A*. Retorna (tempo_ms, expandidos, custo)."""
    inicio = time.perf_counter_ns()
    _, custo, expandidos = astar(grid, origem, destino)
    fim = time.perf_counter_ns()
    return (fim - inicio) / 1e6, expandidos, custo


def executar(rodadas: int, tamanhos) -> list[list]:
    linhas_csv = []

    for cenario in ("melhor", "medio", "pior"):
        for lado, rotulo in tamanhos:
            n_celulas = lado * lado

            if cenario == "medio":
                # Aquecimento com grades que NÃO entram na medição.
                for seed in SEEDS_AQUECIMENTO[:AQUECIMENTO]:
                    grid, origem, destino, _ = caso_medio(lado, seed)
                    cronometrar(grid, origem, destino)
                for rodada in range(1, rodadas + 1):
                    grid, origem, destino, seed_usada = caso_medio(lado, rodada)
                    tempo_ms, expandidos, custo = cronometrar(grid, origem, destino)
                    linhas_csv.append([
                        LINGUAGEM, cenario, rotulo, lado, n_celulas,
                        rodada, seed_usada, f"{tempo_ms:.6f}", expandidos, custo,
                    ])
            else:
                gerador = melhor_caso if cenario == "melhor" else pior_caso
                grid, origem, destino = gerador(lado)
                for _ in range(AQUECIMENTO):
                    cronometrar(grid, origem, destino)
                for rodada in range(1, rodadas + 1):
                    tempo_ms, expandidos, custo = cronometrar(grid, origem, destino)
                    linhas_csv.append([
                        LINGUAGEM, cenario, rotulo, lado, n_celulas,
                        rodada, "", f"{tempo_ms:.6f}", expandidos, custo,
                    ])

            print(f"[{LINGUAGEM}] {cenario:<6} lado={lado:<4} ({rotulo}) ok",
                  file=sys.stderr)

    return linhas_csv


def main() -> None:
    rapido = "--rapido" in sys.argv
    rodadas = 5 if rapido else RODADAS
    tamanhos = [t for t in TAMANHOS if t[1] != "intermediaria"] if rapido else TAMANHOS

    linhas_csv = executar(rodadas, tamanhos)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(CABECALHO)
        escritor.writerows(linhas_csv)

    print(f"{len(linhas_csv)} medições gravadas em {ARQUIVO_SAIDA}", file=sys.stderr)


if __name__ == "__main__":
    main()
