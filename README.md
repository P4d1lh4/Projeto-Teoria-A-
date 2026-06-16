# Projeto Teoria da Computação — Algoritmo A* (A-estrela)

Implementação e análise de complexidade do algoritmo **A\*** em **Python** e **JavaScript**,
para a disciplina Teoria da Computação (Prof. Daniel Bezerra).

O A* resolve o problema do **caminho mínimo entre dois pontos** em um grafo, guiado por uma
heurística admissível. Neste projeto ele é aplicado a grades 2D (mapas com obstáculos),
com movimento em 4 direções, custo unitário e heurística de **distância de Manhattan**.

## Estrutura do repositório

```
├── python/              # Implementação em Python
│   ├── astar.py         # Algoritmo A*
│   ├── scenarios.py     # Geradores de cenário (melhor/médio/pior caso) + PRNG
│   ├── benchmark.py     # Protocolo experimental (30 rodadas por cenário/tamanho)
│   ├── charts.py        # Geração dos gráficos (matplotlib)
│   └── test_astar.py    # Testes (unittest)
├── javascript/          # Implementação em JavaScript (Node >= 18)
│   ├── astar.js         # Algoritmo A* + heap binário
│   ├── scenarios.js     # Geradores de cenário (idênticos aos de Python)
│   ├── benchmark.js     # Protocolo experimental
│   └── test/astar.test.js  # Testes (node:test)
├── tools/
│   └── verificar_equivalencia.py  # Prova que Py e JS processam entradas idênticas
├── results/             # CSVs das medições + gráficos gerados
├── docs/
│   ├── relatorio.md     # Relatório (base para o PDF)
│   ├── slides.md        # Protótipo dos slides (formato Marp)
│   └── slides.html      # Protótipo dos slides (abrir no navegador)
└── demo/
    └── index.html       # Demonstração visual interativa do A* (para a apresentação)
```

## Como executar

### Testes

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

### Benchmarks (protocolo: 30 rodadas × 3 cenários × tamanhos)

```bash
python python/benchmark.py     # gera results/resultados_python.csv
node javascript/benchmark.js   # gera results/resultados_javascript.csv
```

### Gráficos e tabelas

```bash
python python/charts.py        # gera results/graficos/*.png e docs/tabelas_resultados.md
```

Requisito: `matplotlib` (`pip install matplotlib`).

## Cenários de teste

| Cenário | Entrada | Comportamento esperado |
|---|---|---|
| **Melhor caso** | Grade vazia, origem e destino na mesma linha | Heurística perfeita: expande só o caminho reto — Ω(√n) |
| **Caso médio** | Obstáculos aleatórios (densidade 25%), 30 grades distintas por tamanho | Exploração parcial da grade |
| **Pior caso** | Labirinto em serpentina | Heurística não ajuda: expande ~todas as células livres — O(n log n) |

`n` = número de células da grade. Tamanhos nomeados: pequena (51×51), média (151×151), grande (301×301).

## Demonstração visual

Abra `demo/index.html` no navegador para ver o A* explorando a grade em tempo real
(útil para a apresentação oral).

## Integrantes
* Arthur Lins da Gama
* Arthur Pedrosa Padilha
* Pedro Torjal de Medeiros
