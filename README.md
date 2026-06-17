# Projeto Teoria da Computação — Algoritmo A* (A-estrela)

Implementação e análise de complexidade do algoritmo **A\*** em **Python** e **JavaScript**,
para a disciplina Teoria da Computação (Prof. Daniel Bezerra — CESAR School, 2026).

**Equipe:** Arthur Padilha, Pedro Tojal, Arthur Lins, Luis Guilherme

O A* resolve o problema do **caminho mínimo entre dois pontos** em um grafo, guiado por uma
heurística admissível. Neste projeto ele é aplicado a grades 2D (mapas com obstáculos),
com movimento em 4 direções, custo unitário e heurística de **distância de Manhattan**.

## Entregas

| Arquivo | Descrição |
|---|---|
| `docs/relatorio_astar_abnt.docx` | Relatório completo formatado (ABNT NBR 14724) |
| `docs/slides.html` | Slides da apresentação (abrir no navegador) |
| `demo/index.html` | Demonstração visual interativa do A* |

## Estrutura do repositório

```
├── python/
│   ├── astar.py             # Algoritmo A*
│   ├── scenarios.py         # Geradores de cenário (melhor/médio/pior caso) + PRNG
│   ├── benchmark.py         # Protocolo experimental (30 rodadas × cenário × tamanho)
│   ├── charts.py            # Geração dos gráficos (matplotlib)
│   └── test_astar.py        # Testes (unittest)
├── javascript/
│   ├── astar.js             # Algoritmo A* + heap binário próprio
│   ├── scenarios.js         # Geradores de cenário (idênticos aos de Python)
│   ├── benchmark.js         # Protocolo experimental
│   └── test/astar.test.js   # Testes (node:test)
├── tools/
│   └── verificar_equivalencia.py  # Prova que Py e JS processam entradas idênticas
├── results/
│   ├── resultados_python.csv      # 540 medições Python (30 rodadas × 3 cenários × 6 tamanhos)
│   ├── resultados_javascript.csv  # 540 medições JavaScript
│   ├── resumo.csv                 # Médias e desvios-padrão agregados
│   └── graficos/                  # 7 gráficos PNG gerados por charts.py
├── docs/
│   ├── relatorio_astar_abnt.docx  # Relatório final (ABNT)
│   ├── relatorio_abnt.md          # Fonte Markdown do relatório
│   ├── gerar_relatorio.py         # Script que gerou o DOCX (python-docx)
│   ├── slides.md                  # Fonte dos slides (Marp)
│   ├── slides.html                # Slides prontos para apresentar (reveal.js)
│   └── tabelas_resultados.md      # Tabelas geradas automaticamente por charts.py
└── demo/
    └── index.html                 # Demonstração visual interativa (para a apresentação)
```

## Como executar

### Pré-requisitos

- Python 3.10+ com `matplotlib`: `pip install matplotlib`
- Node.js 18+

### Testes unitários

```bash
# Python
python -m unittest discover -s python -v

# JavaScript
node --test javascript/test/astar.test.js
```

### Verificação de equivalência entre as linguagens

Confirma que as duas implementações geram as mesmas grades (mesmo PRNG), expandem o
mesmo número de nós e encontram caminhos de mesmo custo:

```bash
python tools/verificar_equivalencia.py
```

### Benchmarks

```bash
python python/benchmark.py     # → results/resultados_python.csv
node javascript/benchmark.js   # → results/resultados_javascript.csv
```

Modo rápido (5 rodadas, apenas os 3 tamanhos nomeados):

```bash
python python/benchmark.py --rapido
```

### Gráficos e tabelas

```bash
python python/charts.py        # → results/graficos/*.png  +  docs/tabelas_resultados.md
```

## Cenários de teste

| Cenário | Entrada | Complexidade |
|---|---|---|
| **Melhor caso** | Grade vazia, caminho reto | Θ(√n) — expande exatamente √n vértices |
| **Caso médio** | Obstáculos aleatórios 25%, 30 grades distintas | ≈ Θ(n) — ~8% das células |
| **Pior caso** | Labirinto em serpentina | Θ(n log n) — ~50% das células |

`n` = número de células da grade. Tamanhos: pequena (51×51), média (151×151), grande (301×301).

## Demonstração visual

Abra `demo/index.html` no navegador para ver o A* explorando a grade em tempo real
(útil para a apresentação oral).
