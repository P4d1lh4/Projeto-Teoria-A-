---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section { font-size: 26px; }
  h1 { color: #1a4f8b; }
  h2 { color: #1a4f8b; }
  table { font-size: 22px; }
  img { background: #fff; }
---

<!--
PROTÓTIPO dos slides — base para a apresentação da equipe.
Renderizável com Marp (https://marp.app): VS Code + extensão "Marp for VS Code",
ou `npx @marp-team/marp-cli docs/slides.md -o slides.pdf`.
Há também uma versão pronta para navegador em docs/slides.html.
-->

# Algoritmo A* (A-estrela)
## Análise de Complexidade e Tempo de Execução

**Teoria da Computação** — Prof. Daniel Bezerra

Equipe: _(nomes dos integrantes)_

Python 3.13 × JavaScript (Node 22)

---

## O problema: caminho mínimo

- Dado um mapa com obstáculos, **qual o caminho mais curto** entre dois pontos?
- Modelo: grade 2D → grafo (células livres = vértices, vizinhança em
  4 direções, custo 1 por passo)
- Onde aparece: **jogos**, **robótica**, **GPS**, planejamento, puzzles

**Dijkstra** resolve… mas explora "em círculos" ao redor da origem.
Podemos fazer melhor se **soubermos a direção do destino**.

---

## A ideia do A*

Busca de melhor-primeiro ordenada por:

### f(v) = g(v) + h(v)

- **g(v)** — custo real da origem até v
- **h(v)** — estimativa heurística de v até o destino
- h ≡ 0 ⟹ A* vira o Dijkstra

Heurística usada: **distância de Manhattan**
h(v) = |Δlinha| + |Δcoluna|

---

## Por que o resultado é ótimo?

A heurística de Manhattan (grade, 4 direções, custo 1) é:

- **Admissível** — nunca superestima o custo real
  (cada passo reduz a distância de Manhattan em no máximo 1)
- **Consistente** — h(u) ≤ 1 + h(v) para vizinhos u, v
  ⟹ cada vértice é expandido **no máximo uma vez**

> Com heurística admissível e consistente, o primeiro caminho
> encontrado pelo A* é **garantidamente o de menor custo**.

---

## Pseudocódigo

```text
A*(grade, origem, destino):
    aberta <- heap-mínimo ordenado por (f, h, ordem)
    g[origem] <- 0; insere origem com f = h(origem)
    enquanto aberta não vazia:
        v <- remove-mínimo(aberta)
        se v já expandido: continua        # lazy deletion
        marca v como expandido
        se v = destino: retorna caminho (pais)
        para cada vizinho u livre de v:
            g' <- g[v] + 1
            se g' < g[u]:
                g[u] <- g'; pai[u] <- v
                insere u com f = g' + h(u)
```

Heap binário + *lazy deletion* — idêntico nas duas linguagens.

---

## Classificação assintótica

Grade com **n células** ⟹ V = n, E = O(n); heap binário: O(log n) por operação.

| Limite | Valor | Situação |
|---|---|---|
| **Big-O** | **O(n log n)** | heurística não ajuda: tudo passa pelo heap |
| **Big-Ω** | **Ω(L)** | heurística perfeita: só o caminho (L = √n aqui) |
| **Big-Θ** | por caso | pior: Θ(n log n) · melhor: Θ(√n log n) · médio: ≈ Θ(n) |

Memória: **O(n)**. Em espaços de estados implícitos: **O(b^d)** (exponencial).

---

## Cenários dos experimentos

| Cenário | Entrada | Comportamento |
|---|---|---|
| **Melhor** | grade vazia, destino na mesma linha | expande só a linha reta (√n nós) |
| **Médio** | obstáculos aleatórios 25%, 30 grades/tamanho | ~8% da grade expandida |
| **Pior** | labirinto em serpentina | expande **todas** as células livres |

Tamanhos: **51×51** (pequena) · **151×151** (média) · **301×301** (grande)
(+ 101, 201, 251 para as curvas)

---

## Metodologia

- **30 rodadas** medidas por (cenário × tamanho × linguagem)
  + 3 de aquecimento descartadas (JIT do V8!)
- Relógios de alta precisão: `time.perf_counter_ns()` / `process.hrtime.bigint()`
- Hardware: i5-10500 (6C/12T), 16 GB RAM, Windows 11 Pro

**Comparação justa entre linguagens:**
- mesmo PRNG (mulberry32) bit a bit ⟹ **grades idênticas** (hash conferido)
- mesmo desempate no heap ⟹ **mesmos nós expandidos, na mesma ordem**
- verificado automaticamente: `tools/verificar_equivalencia.py`

---

## Resultados — pior caso × teoria

![h:480 center](../results/graficos/aderencia_pior.png)

Medições caem sobre a reta **c·n·log n** (escala log-log) nas duas linguagens.

---

## Resultados — análise de casos

![h:480 center](../results/graficos/casos_python.png)

Três regimes bem separados: pior ≫ médio ≫ melhor — como previsto.

---

## Resultados — trabalho algorítmico

![h:480 center](../results/graficos/nos_expandidos.png)

Nós expandidos **idênticos** em Python e JavaScript — por construção.

---

## Resultados — Python × JavaScript

![h:420 center](../results/graficos/comparacao_linguagens.png)

| Grade 301×301 | Python | JavaScript | Razão |
|---|---|---|---|
| Pior caso | 94,1 ms | 20,9 ms | **4,5×** |

JIT do V8 × interpretador do CPython — mesmo trabalho, custo por operação menor.

---

## Curiosidade: quando o "lento" ganha

Melhor caso, grade 51×51 (51 nós expandidos):

- Python: **0,166 ms** — JavaScript: **0,261 ms**

Em execuções submilissegundo, **custos fixos do runtime** dominam
o termo assintótico.

> Análise assintótica descreve o **crescimento**,
> não o valor absoluto em entradas pequenas.

---

## Aplicabilidade e limitações

**Brilha quando** há heurística admissível barata:
jogos, robótica, GPS, planejamento, puzzles.

**Limitações:**
- memória O(V) → IDA*, SMA*, fringe search
- heurística fraca → degenera para Dijkstra (nosso pior caso!)
- mapas dinâmicos → D* Lite
- consultas repetidas → pré-processamento (contraction hierarchies)

---

## Reflexão: P, NP e vizinhos

- Caminho mínimo (pesos ≥ 0) ∈ **P** — decisão "custo ≤ k?" é polinomial
- Variantes **NP-completas/difíceis**:
  - caminho simples **mais longo** (contém Hamiltoniano)
  - TSP, caminho com restrição de recursos
  - *multi-agent pathfinding* ótimo
  - (n²−1)-puzzle ótimo — o A* continua **correto**, mas exponencial: O(b^d)

> O mesmo algoritmo: polinomial em P, exponencial sobre espaços NP-difíceis.
> Heurística muda constantes — **nunca a classe de complexidade**.

---

## Conclusões

- A* = Dijkstra + heurística: **ótimo** com h admissível/consistente
- Teoria confirmada na prática: pior caso ⟶ reta n log n em log-log
- Heurística importa: melhor caso expande √n nós; pior caso, todos
- JavaScript 4,5–6,4× mais rápido **no pior caso** (JIT), mas
  **mesma assintótica** — linguagem muda a constante, não a curva
- Demo interativa: `demo/index.html`

**Repositório:** github.com/P4d1lh4/Projeto-Teoria-A-

---

## Referências

- Hart, Nilsson & Raphael (1968) — *A Formal Basis for the Heuristic
  Determination of Minimum Cost Paths*
- Russell & Norvig — *AIMA*, 4ª ed., cap. 3
- Cormen et al. — *Introduction to Algorithms*, 4ª ed.
- Ratner & Warmuth (1990) — NP-dificuldade do (n²−1)-puzzle
- Garey & Johnson (1979) — *Computers and Intractability*
