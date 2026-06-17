&lt;!--
  RELATÓRIO — ALGORITMO A* (A-ESTRELA)
  Disciplina: Teoria da Computação — Prof. Daniel Bezerra
  CESAR School — Ciência da Computação
  Equipe: Arthur Padilha, Pedro Tojal, Arthur Lins, Luis Guilherme
  2026

  Para gerar o PDF:
      pandoc relatorio_abnt.md -o relatorio_astar_abnt.pdf \
             --pdf-engine=xelatex \
             -V geometry:margin=3cm \
             -V fontsize=12pt \
             -V lang=pt-BR
--&gt;

---

&lt;center&gt;

**CESAR SCHOOL**
**CIÊNCIA DA COMPUTAÇÃO**
**TEORIA DA COMPUTAÇÃO**

&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;

# ALGORITMO A\* (A-ESTRELA)

Análise teórica e experimental do caminho mínimo em grades:
implementações em Python e JavaScript

&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;

Arthur Padilha
Pedro Tojal
Arthur Lins
Luis Guilherme

Prof. Daniel Bezerra

&lt;br&gt;&lt;br&gt;

**Recife**
**2026**

&lt;/center&gt;

---

## SUMÁRIO

1. Introdução .....3
2. O Algoritmo A\* .....4
   - 2.1 Definição e objetivo .....4
   - 2.2 Funcionamento passo a passo .....4
   - 2.3 Estrutura de dados: heap binário de mínimo .....5
   - 2.4 Pseudocódigo .....6
   - 2.5 Complexidade computacional (O, Ω e Θ) .....6
3. Metodologia Experimental .....8
   - 3.1 Implementações .....8
   - 3.2 Cenários de teste e geração das entradas .....8
   - 3.3 Tamanhos avaliados .....9
   - 3.4 Protocolo de medição .....9
   - 3.5 Ambiente de execução .....10
   - 3.6 Resumo dos cenários executados .....10
4. Resultados e Análise dos Gráficos .....13
   - 4.1 Curvas de tempo por cenário .....13
   - 4.2 Comparação entre Python e JavaScript .....16
   - 4.3 Trabalho algorítmico: nós expandidos .....17
   - 4.4 Validação do modelo teórico .....18
5. Aplicabilidade: Eficiência e Limitações .....19
   - 5.1 Contextos de eficiência e aplicações .....19
   - 5.2 Limitações .....20
6. Reflexão Teórica: Classes de Complexidade .....21
   - 6.1 O problema pertence à classe P? .....21
   - 6.2 Existe uma versão NP do problema? .....21
   - 6.3 Problemas semelhantes NP-completos .....22
7. Execução do Projeto .....23
8. Conclusão .....24

REFERÊNCIAS .....25

---

## 1 INTRODUÇÃO

O problema do caminho mínimo é central na Teoria da Computação e em inúmeras aplicações práticas. Em contextos onde se dispõe de um destino conhecido e de uma estimativa do custo restante para alcançá-lo, a busca pode ser guiada de forma muito mais eficiente do que na exploração cega. O algoritmo A\* (lê-se "A-estrela"), proposto por Peter Hart, Nils Nilsson e Bertram Raphael em 1968, formaliza essa intuição: ele ordena a fronteira de busca por uma função f(v) = g(v) + h(v), onde g(v) é o custo real acumulado da origem até v e h(v) é uma estimativa heurística do custo de v até o destino. Quando a heurística é admissível — nunca superestima o custo real — o A\* é garantidamente ótimo: o primeiro caminho encontrado é o de menor custo. Quando é também consistente (monótona), cada vértice é expandido no máximo uma vez, eliminando retrabalho.

Este trabalho tem como objetivo estudar o algoritmo A\* sob duas perspectivas complementares. Na perspectiva teórica, descreve-se o que o algoritmo faz, como funciona passo a passo, qual a estrutura de dados empregada e qual a sua complexidade assintótica nas notações O, Ω e Θ. Na perspectiva experimental, o algoritmo foi implementado em duas linguagens de programação — Python e JavaScript (executado no Node.js) — e submetido a um conjunto de experimentos controlados com o objetivo de medir o tempo de execução em três cenários distintos e validar empiricamente o comportamento previsto pela teoria.

O domínio escolhido para os experimentos é uma **grade 2D com obstáculos**: cada célula livre é um vértice, vizinha das células livres adjacentes em quatro direções (cima, baixo, esquerda, direita), com custo unitário por passo. A heurística empregada é a **distância de Manhattan**, h(v) = |v.linha − destino.linha| + |v.coluna − destino.coluna|, que é admissível e consistente para movimento em quatro direções com custo unitário — garantindo a otimalidade do algoritmo.

O relatório está organizado da seguinte forma. A Seção 2 apresenta a fundamentação teórica do algoritmo. A Seção 3 detalha a metodologia experimental, incluindo os cenários de teste, a geração das entradas, os tamanhos avaliados, o ambiente de execução e o protocolo de medição. A Seção 4 discute os resultados, analisando individualmente cada gráfico gerado. A Seção 5 aborda a aplicabilidade do algoritmo, com seus contextos de eficiência e limitações. A Seção 6 traz a reflexão teórica sobre as classes de complexidade P e NP. A Seção 7 explica como executar os códigos do projeto e a Seção 8 apresenta as conclusões.

---

## 2 O ALGORITMO A\*

### 2.1 Definição e objetivo

O algoritmo A\* resolve o problema do **caminho de menor custo entre dois vértices** de um grafo com pesos não negativos nas arestas, utilizando uma **função heurística** que estima o custo restante até o destino. Enquanto o algoritmo de Dijkstra explora todos os vértices em ordem crescente de distância à origem — comportamento equivalente ao A\* com heurística h ≡ 0 —, o A\* "puxa" a busca na direção do destino, expandindo primeiro os vértices com maior potencial de levar a um caminho ótimo. Isso pode reduzir drasticamente o número de vértices processados, especialmente quando a heurística é precisa.

Duas propriedades da heurística são suficientes para garantir a otimalidade:

- **Admissibilidade:** h(v) ≤ custo_real(v, destino) para todo vértice v. A heurística nunca superestima, portanto o algoritmo nunca descarta prematuramente um caminho ótimo.
- **Consistência (monotonicidade):** h(u) ≤ custo(u, v) + h(v) para toda aresta (u, v). Com consistência, a sequência de valores f ao longo de qualquer caminho explorado é não decrescente, e cada vértice é expandido no máximo uma vez — o que reduz significativamente o trabalho total.

A distância de Manhattan satisfaz ambas as propriedades para movimento em quatro direções com custo unitário: cada passo reduz a distância de Manhattan em exatamente 1 (se for na direção certa) ou aumenta em 1 (se for perpendicular), portanto a estimativa nunca excede o custo real.

### 2.2 Funcionamento passo a passo

O funcionamento do algoritmo A\* pode ser resumido nos seguintes passos:

- **Inicialização:** o custo real g(origem) é definido como 0. O vértice de origem é inserido na fila de prioridade (lista aberta) com prioridade f(origem) = g(origem) + h(origem) = h(origem). Todos os demais g-scores são considerados infinitos.

- **Extração do mínimo:** remove-se da lista aberta o vértice v com o menor valor de f. Se v já foi expandido anteriormente (entrada obsoleta — ver *lazy deletion* abaixo), a entrada é descartada e passa-se para a próxima.

- **Verificação do objetivo:** se v é o vértice de destino, o algoritmo retorna o caminho reconstruído pela cadeia de ponteiros de pai e o custo g(v).

- **Expansão dos vizinhos:** para cada vizinho u de v acessível (célula livre e dentro da grade), calcula-se o custo tentativo g' = g(v) + 1. Se g' < g(u) (caminho melhor encontrado), atualiza-se g(u), registra-se v como pai de u e insere-se u na lista aberta com prioridade f(u) = g' + h(u).

- **Repetição:** os passos de extração e expansão se repetem até que a lista aberta fique vazia (nenhum caminho existe) ou o destino seja extraído.

Uma técnica importante de implementação é a **lazy deletion** (deleção preguiçosa): como um vértice pode ser inserido na fila múltiplas vezes com g-scores diferentes (quando um caminho melhor é descoberto), cada extração verifica se a entrada é obsoleta. Em vez de remover elementos do meio do heap — operação custosa —, as entradas obsoletas são simplesmente descartadas ao serem extraídas. Essa técnica preserva a complexidade assintótica e simplifica a implementação.

### 2.3 Estrutura de dados: heap binário de mínimo

A eficiência do algoritmo depende fundamentalmente da estrutura usada para extrair, a cada passo, o vértice com menor valor de f. Neste trabalho utilizou-se uma **fila de prioridade implementada como heap binário de mínimo**, que garante inserção e remoção do menor elemento em tempo O(log n), onde n é o número de elementos no heap.

O critério de comparação entre elementos foi definido com três níveis de desempate: (1) menor f = g + h, (2) menor h (favorece vértices mais próximos do destino entre aqueles com mesmo custo total), (3) menor ordem de inserção (garante determinismo total na expansão). O desempate determinístico é essencial para a comparabilidade entre as duas linguagens: com o mesmo critério, as implementações expandem exatamente os mesmos vértices, na mesma ordem.

Na implementação em **Python**, utilizou-se o módulo padrão `heapq`. Na implementação em **JavaScript**, como a linguagem não oferece uma fila de prioridade nativa, foi desenvolvida uma classe `MinHeap` própria, com os métodos de subida (*bubble up*) e descida (*sink down*) que mantêm a propriedade do heap. Ambas as implementações utilizam `Map` e `Set` (ou dicionários em Python) para armazenar g-scores, ponteiros de pai e o conjunto de vértices já expandidos — estruturas com acesso médio O(1), que não alteram a complexidade assintótica.

### 2.4 Pseudocódigo

A seguir, o pseudocódigo do algoritmo implementado:

```
A*(grade, origem, destino):
    aberta  <- heap-mínimo ordenado por (f, h, ordem de inserção)
    g[origem] <- 0
    insere origem na aberta com f = h(origem)

    enquanto aberta não vazia:
        (f, h, _, v) <- extrai_minimo(aberta)
        se v já foi expandido: continua    # entrada obsoleta (lazy deletion)
        marca v como expandido

        se v = destino:
            retorna (caminho reconstruído pelos pais, g[v])

        para cada vizinho u de v (4 direções, livre, dentro da grade):
            g' <- g[v] + 1
            se g' < g[u]:                  # caminho melhor até u
                g[u] <- g'
                pai[u] <- v
                hu <- manhattan(u, destino)
                insere u na aberta com f = g' + hu

    retorna "sem caminho"
```

### 2.5 Complexidade computacional (O, Ω e Θ)

A análise de complexidade descreve como o tempo de execução cresce em função do tamanho da entrada. Para o A\* em grades, define-se **n** como o número total de células (n = lado²) e observa-se que cada célula livre tem no máximo 4 vizinhos, logo o número de arestas E = O(n). Com heap binário, cada operação de inserção ou remoção custa O(log n).

**Limite superior — O(n log n):** no pior caso, todos os n vértices passam pelo heap. Cada vértice pode ser inserido no máximo uma vez por vizinho que descobre um caminho melhor (no máximo 4 inserções por vértice), e cada inserção/remoção custa O(log n). O número total de operações no heap é portanto O(4n) = O(n), e o custo total O(n log n). Nenhuma execução ultrapassa esse limite, independentemente da configuração da grade ou da heurística usada.

**Limite inferior — Ω(L):** o algoritmo precisa, obrigatoriamente, expandir cada vértice do caminho ótimo pelo menos uma vez — caso contrário, o caminho não seria retornado. Se o caminho ótimo tem comprimento L (em passos), são necessárias pelo menos L + 1 expansões. Cada expansão envolve ao menos uma operação de heap de custo O(log n), portanto o limite inferior é Ω(L · log n). No cenário de melhor caso deste trabalho, o caminho reto na grade tem L = lado − 1 ≈ √n passos, resultando em Ω(√n · log n) — empiricamente aproximado por Θ(√n), pois log n cresce muito lentamente para os tamanhos testados.

**Limite justo — Θ por caso:** não existe um limite Θ global para o A\*, pois os limites superior e inferior não coincidem para todo conjunto de entradas. A análise deve ser feita por caso:

- **Melhor caso** (grade vazia, caminho reto): a heurística de Manhattan é perfeita — ela assume exatamente o valor do custo real para todos os vértices do caminho reto. O A\* expande apenas os L + 1 ≈ √n + 1 vértices do caminho, e nenhum outro; o tempo é Θ(√n · log n), empiricamente Θ(√n). Confirmado pelos dados: 51, 151 e 301 expansões para grades 51×51, 151×151 e 301×301, respectivamente.

- **Caso médio** (obstáculos aleatórios 25%): a heurística orienta a busca, mas os desvios em torno dos obstáculos forçam exploração extra. Os experimentos mostram aproximadamente 8% das células expandidas (251 de 2601, 1768 de 22801, 6756 de 90601) — fração aproximadamente constante, independente de n. O tempo é portanto ≈ Θ(n · log n) com constante pequena, empiricamente ajustado como Θ(n).

- **Pior caso** (labirinto em serpentina): a heurística aponta "para baixo" enquanto o caminho precisa percorrer todos os corredores do labirinto em zigue-zague. O A\* expande exatamente os vértices no único caminho possível, que percorre aproximadamente metade das células da grade (1301, 11401 e 45601 expansões para n = 2601, 22801 e 90601, respectivamente — cerca de n/2 vértices). O tempo é Θ(n log n).

A **complexidade de espaço** é Θ(n) em todos os casos: o mapa de g-scores, o conjunto de vértices expandidos, o mapa de ponteiros de pai e o heap crescem no máximo até cobrir os n vértices da grade.

Esse comportamento teórico é exatamente o que se busca confirmar nos experimentos da Seção 4: espera-se que o tempo cresça como √n no melhor caso, linearmente no caso médio e como n log n no pior caso — e que grafos com mais vértices expandidos sejam consideravelmente mais lentos que grafos onde a heurística guia diretamente ao destino.

---

## 3 METODOLOGIA EXPERIMENTAL

### 3.1 Implementações

O algoritmo foi implementado de forma equivalente em duas linguagens: Python (arquivo `python/astar.py`) e JavaScript executado no Node.js (arquivo `javascript/astar.js`). Ambas as versões utilizam heap binário de mínimo com o mesmo critério de desempate — (f, h, ordem de inserção) — e os mesmos mapeamentos para g-scores, ponteiros de pai e conjunto de expandidos.

Para garantir uma comparação justa entre as linguagens — medindo a diferença de desempenho do *runtime* e não de implementação —, adotaram-se três mecanismos de equivalência: (1) o mesmo gerador pseudoaleatório (*mulberry32*, reproduzido bit a bit nas duas linguagens, incluindo aritmética módulo 2³²) garante **grades idênticas**; (2) o mesmo critério de desempate no heap garante a **expansão dos mesmos vértices, na mesma ordem**; (3) um script de verificação (`tools/verificar_equivalencia.py`) confirma automaticamente, via hash FNV-1a das grades e comparação de nós expandidos e custos, que as saídas das duas implementações são idênticas. Os CSVs de resultados confirmam: nós expandidos e custos de caminho são **idênticos** nas duas linguagens em todas as 540 medições (30 rodadas × 3 cenários × 6 tamanhos × 2 linguagens).

### 3.2 Cenários de teste e geração das entradas

Para avaliar o algoritmo em condições que representem seus limites assintóticos, foram definidos três cenários que correspondem ao melhor caso, caso médio e pior caso em termos de nós expandidos.

- **Melhor caso — grade vazia:** a grade não contém obstáculos. A origem é a célula central da primeira coluna e o destino é a célula central da última coluna, ambos na mesma linha (linha do meio). O caminho ótimo é uma linha reta com L = lado − 1 passos. A heurística de Manhattan é exata para todo vértice nessa linha, e ligeiramente superestimada (em relação à rota direta) para os vértices fora dela — garantindo que o A\* expanda **exatamente** os L + 1 vértices do caminho reto, sem explorar nenhum outro.

- **Caso médio — obstáculos aleatórios (25%):** cada célula da grade é bloqueada com probabilidade 25%, usando o gerador *mulberry32* com a semente correspondente ao número da rodada (sementes 1 a 30). A origem é o canto superior esquerdo e o destino é o canto inferior direito. Se a grade sorteada não possuir caminho entre os cantos (o que pode ocorrer com obstáculos aleatórios), tenta-se a próxima semente derivada até encontrar uma grade conexa. A regra de tentativa é idêntica nas duas linguagens, garantindo que processem as mesmas grades. Esse cenário representa uma situação realista: a heurística orienta a busca, mas os desvios em torno dos obstáculos forçam exploração adicional.

- **Pior caso — labirinto em serpentina:** a grade contém paredes horizontais completas nas linhas ímpares (1, 3, 5, ...), cada uma com uma única abertura que alterna entre o extremo direito e o extremo esquerdo. O trajeto entre os cantos opostos (superior esquerdo e inferior direito) obriga o algoritmo a percorrer todos os corredores em zigue-zague. A heurística de Manhattan aponta sistematicamente "para baixo" (em direção ao destino), enquanto o caminho real exige ir e voltar por cada corredor. O resultado é que o A\* expande todos os vértices no único caminho possível — aproximadamente n/2 vértices —, degenerando para o comportamento do Dijkstra sem benefício heurístico efetivo.

### 3.3 Tamanhos avaliados

Cada cenário foi executado em seis tamanhos de grade, definidos pelo comprimento do lado: **51, 101, 151, 201, 251 e 301** células. Isso corresponde a grades com **2.601, 10.201, 22.801, 40.401, 63.001 e 90.601** células totais, respectivamente. Os três tamanhos nomeados — **pequena (51×51), média (151×151) e grande (301×301)** — são os exigidos pela especificação; os três intermediários (101, 201, 251) foram incluídos para dar maior resolução às curvas dos gráficos e facilitar a verificação visual da tendência assintótica.

### 3.4 Protocolo de medição

Cada combinação de cenário e tamanho foi executada **30 vezes (rodadas)**, totalizando 18 combinações por linguagem e 540 medições no total. Para cada rodada mediu-se o tempo de execução do algoritmo, excluindo a geração da grade (que é realizada antes do início da cronometragem). A repetição em 30 rodadas reduz o efeito de ruídos do sistema operacional e do compilador JIT.

Antes das 30 rodadas medidas, realizaram-se **3 rodadas de aquecimento descartadas** em ambas as linguagens. O aquecimento é especialmente importante no Node.js, onde o compilador JIT do motor V8 otimiza o código nas primeiras execuções: sem aquecimento, as primeiras rodadas incluiriam o custo de compilação, distorcendo as medições. No Python, o aquecimento também é útil para aquecer caches do interpretador e do sistema operacional.

Para o **caso médio**, cada rodada usa uma grade diferente (semente = número da rodada), de modo que as 30 medições refletem tanto a variabilidade do tempo de execução quanto a variabilidade das instâncias — por isso o desvio-padrão do caso médio é maior do que nos cenários determinísticos.

Para garantir a validade das medições, utilizaram-se funções de cronometragem de **alta precisão**:
- **Python:** `time.perf_counter_ns()` — contador monotônico com resolução de nanossegundos;
- **JavaScript:** `process.hrtime.bigint()` — equivalente em Node.js.

Ambas cronometram exclusivamente a chamada do algoritmo, sem incluir a geração da grade.

### 3.5 Ambiente de execução

Como o tempo de execução é sensível ao hardware e ao sistema operacional, todos os experimentos foram realizados na mesma máquina, cujas especificações são:

- **Processador:** Intel Core i5-10500 @ 3,10 GHz (6 núcleos / 12 *threads*).
- **Memória:** 16 GB de RAM.
- **Sistema operacional:** Windows 11 Pro (build 26200).
- **Interpretador Python:** Python 3.13.7 (CPython).
- **Ambiente JavaScript:** Node.js v22.21.1 (motor V8).

Os benchmarks foram executados de forma isolada: um cenário por vez, em processo dedicado, sem outras aplicações pesadas em execução concorrente. O tempo medido refere-se exclusivamente à execução do algoritmo, excluindo a geração das grades.

### 3.6 Resumo dos cenários executados

As Tabelas 1, 2 e 3 consolidam as estatísticas obtidas em cada tamanho e linguagem para os três cenários (média e desvio-padrão das 30 rodadas, além dos valores mínimo e máximo). Os dados completos estão disponíveis nos arquivos `results/resultados_python.csv` e `results/resultados_javascript.csv`.

---

**Tabela 1 – Tempos de execução – Melhor caso (grade vazia, caminho reto) (ms)**

| Linguagem | Tam. | n (células) | Nós expand. | Média ± DP (ms) | Mín (ms) | Máx (ms) |
|-----------|------|-------------|-------------|-----------------|----------|----------|
| Python | pequena | 2.601 | 51 | 0,166 ± 0,004 | 0,160 | 0,177 |
| JavaScript | pequena | 2.601 | 51 | 0,261 ± 0,205 | 0,147 | 1,215 |
| Python | média | 22.801 | 151 | 0,704 ± 0,212 | 0,522 | 1,089 |
| JavaScript | média | 22.801 | 151 | 0,379 ± 0,115 | 0,300 | 0,716 |
| Python | grande | 90.601 | 301 | 1,149 ± 0,051 | 1,125 | 1,413 |
| JavaScript | grande | 90.601 | 301 | 0,338 ± 0,067 | 0,259 | 0,507 |

Fonte: elaborado pelos autores (2026).

---

**Tabela 2 – Tempos de execução – Caso médio (obstáculos aleatórios 25%) (ms)**

| Linguagem | Tam. | n (células) | Nós expand. | Média ± DP (ms) | Mín (ms) | Máx (ms) |
|-----------|------|-------------|-------------|-----------------|----------|----------|
| Python | pequena | 2.601 | ~251 | 0,669 ± 0,203 | 0,374 | 1,107 |
| JavaScript | pequena | 2.601 | ~251 | 0,488 ± 0,168 | 0,244 | 0,803 |
| Python | média | 22.801 | ~1.768 | 5,383 ± 5,982 | 1,712 | 26,910 |
| JavaScript | média | 22.801 | ~1.768 | 1,499 ± 1,943 | 0,392 | 8,606 |
| Python | grande | 90.601 | ~6.756 | 22,101 ± 19,169 | 6,017 | 91,736 |
| JavaScript | grande | 90.601 | ~6.756 | 9,693 ± 6,448 | 3,021 | 31,104 |

Fonte: elaborado pelos autores (2026).

---

**Tabela 3 – Tempos de execução – Pior caso (labirinto em serpentina) (ms)**

| Linguagem | Tam. | n (células) | Nós expand. | Média ± DP (ms) | Mín (ms) | Máx (ms) |
|-----------|------|-------------|-------------|-----------------|----------|----------|
| Python | pequena | 2.601 | 1.301 | 2,235 ± 0,181 | 2,115 | 2,986 |
| JavaScript | pequena | 2.601 | 1.301 | 0,351 ± 0,105 | 0,297 | 0,791 |
| Python | média | 22.801 | 11.401 | 21,556 ± 0,618 | 20,700 | 23,111 |
| JavaScript | média | 22.801 | 11.401 | 4,292 ± 0,543 | 3,464 | 5,827 |
| Python | grande | 90.601 | 45.601 | 94,109 ± 2,263 | 90,638 | 98,685 |
| JavaScript | grande | 90.601 | 45.601 | 20,874 ± 3,672 | 16,637 | 33,033 |

Fonte: elaborado pelos autores (2026).

---

## 4 RESULTADOS E ANÁLISE DOS GRÁFICOS

Esta seção apresenta e interpreta todos os gráficos gerados pelos experimentos, armazenados em `results/graficos/`. Os gráficos estão organizados em quatro grupos: (i) curvas de tempo por cenário com sobreposição do modelo teórico, (ii) análise de casos por linguagem, (iii) comparação direta entre Python e JavaScript e (iv) trabalho algorítmico medido pelos nós expandidos. Para cada figura é fornecida uma análise do que ela mostra e de como confirma ou matiza as previsões teóricas.

### 4.1 Curvas de tempo por cenário

**Figura 1 – Aderência ao modelo teórico: pior caso (labirinto em serpentina)**

![Aderência — pior caso](../results/graficos/aderencia_pior.png)

Fonte: elaborado pelos autores (2026).

O gráfico exibe, em escala log-log, os tempos medidos de Python e JavaScript no pior caso (labirinto em serpentina), sobrepostos à curva teórica c · n · log₂(n), normalizada pelo último ponto de cada série. Em escala log-log, a função n log n manifesta-se como uma reta ligeiramente côncava (crescimento superlinear porém subquadrático). Os pontos medidos de ambas as linguagens acompanham de perto essa reta ao longo de quase duas ordens de grandeza (de n = 2.601 a n = 90.601), confirmando a previsão teórica Θ(n log n) para esse cenário. O desvio-padrão é pequeno nas duas linguagens — Python: ±0,181 ms a ±2,263 ms; JavaScript: ±0,105 ms a ±3,672 ms — evidenciando medições estáveis e reprodutíveis, característica dos cenários determinísticos. A vantagem absoluta do JavaScript é expressiva: para n = 90.601, Python atinge 94,1 ms enquanto JavaScript leva 20,9 ms, uma diferença de 4,5 vezes.

---

**Figura 2 – Aderência ao modelo teórico: caso médio (obstáculos aleatórios 25%)**

![Aderência — caso médio](../results/graficos/aderencia_medio.png)

Fonte: elaborado pelos autores (2026).

O gráfico apresenta os tempos medidos no caso médio sobrepostos à curva c · n (crescimento linear), normalizada pelo último ponto de cada série. A escala log-log transforma a função linear em uma reta de inclinação 1, que os pontos seguem razoavelmente bem. As barras de erro, porém, são consideravelmente maiores do que no pior caso: para n = 90.601, o desvio-padrão do Python chega a 19,169 ms sobre uma média de 22,101 ms, e o do JavaScript a 6,448 ms sobre 9,693 ms. Esse comportamento é esperado e reflete a **variabilidade real do problema**: cada uma das 30 rodadas usa uma grade sorteada diferente, com disposição de obstáculos distinta, e o número de nós expandidos varia de instância para instância. O desvio não é ruído de medição — é a dispersão legítima do caso médio. A fração média de células expandidas (~8%) é aproximadamente constante entre os tamanhos, confirmando o crescimento ≈ linear.

---

**Figura 3 – Aderência ao modelo teórico: melhor caso (grade vazia)**

![Aderência — melhor caso](../results/graficos/aderencia_melhor.png)

Fonte: elaborado pelos autores (2026).

O gráfico apresenta os tempos medidos no melhor caso sobrepostos à curva c · √n, em escala log-log. Para o Python, os pontos seguem bem a reta de inclinação 0,5 esperada (função raiz quadrada em escala log-log), confirmando que o número de nós expandidos — exatamente √n — domina o tempo de execução. O JavaScript, entretanto, apresenta um comportamento distinto: os tempos ficam praticamente constantes em torno de 0,3–0,4 ms para todos os tamanhos testados. Isso revela que, quando o trabalho útil é reduzidíssimo (apenas 51 a 301 nós expandidos), o custo fixo de despacho de funções, alocação de objetos e eventuais verificações do motor V8 domina o tempo total — fenômeno bem documentado em ambientes com JIT e garbage collection. Para n = 2.601 (51 nós expandidos), o Python chega a ser mais rápido que o JavaScript (0,166 ms contra 0,261 ms) justamente por esse motivo: o overhead fixo do V8 supera o ganho do JIT em execuções tão curtas. A situação se inverte a partir de n = 22.801 (151 nós).

---

**Figura 4 – Análise de casos em Python**

![Casos em Python](../results/graficos/casos_python.png)

Fonte: elaborado pelos autores (2026).

O gráfico exibe as três curvas de tempo (melhor, médio e pior caso) para o Python, em escala log-log. As inclinações distintas das três curvas refletem claramente as diferentes classes de crescimento previstas: a curva do melhor caso tem inclinação ≈ 0,5 (crescimento sub-linear, proporcional a √n), a do caso médio tem inclinação ≈ 1 (linear em n) e a do pior caso tem inclinação ligeiramente superior a 1 (superlinear, proporcional a n log n). A separação visual entre as curvas confirma que o cenário tem impacto muito maior no desempenho do que o tamanho da entrada: para n = 90.601, o pior caso é 82 vezes mais lento que o melhor caso (94,1 ms contra 1,15 ms). A variabilidade do caso médio (barras de erro) também é visível no gráfico, enquanto os cenários determinísticos (melhor e pior) apresentam barras muito menores.

---

**Figura 5 – Análise de casos em JavaScript**

![Casos em JavaScript](../results/graficos/casos_javascript.png)

Fonte: elaborado pelos autores (2026).

O gráfico correspondente para JavaScript exibe a mesma estrutura geral de três curvas com inclinações distintas, mas com diferenças relevantes. A curva do melhor caso é praticamente plana — as barras de erro são maiores e o crescimento com n é quase imperceptível —, como já discutido na análise da Figura 3. A curva do pior caso tem inclinação ligeiramente superior a 1 (conforme esperado para n log n) e é claramente dominante para entradas grandes. A proporção entre pior e melhor caso no JavaScript para n = 90.601 é de ~62 vezes (20,9 ms contra 0,34 ms), ligeiramente menor do que no Python (82×), em parte porque o denominador (melhor caso) é menor no JS do que no Python quando n é grande. As barras de erro do caso médio em JavaScript também são proporcionalmente grandes, refletindo a mesma variabilidade legítima de instâncias.

### 4.2 Comparação entre Python e JavaScript

**Figura 6 – Comparação direta entre Python e JavaScript (pior caso)**

![Comparação entre linguagens](../results/graficos/comparacao_linguagens.png)

Fonte: elaborado pelos autores (2026).

O gráfico de barras exibe os tempos médios de Python e JavaScript lado a lado para os três tamanhos nomeados no pior caso. A diferença é expressiva e cresce com n: a razão Python/JavaScript vai de 6,4× na grade pequena (2,235 ms contra 0,351 ms) a 4,5× na grade grande (94,109 ms contra 20,874 ms). A aparente redução da vantagem do JavaScript com o aumento de n deve-se ao aquecimento completo do JIT: nas entradas pequenas, o V8 ainda está otimizando o código nas primeiras rodadas (apesar do aquecimento de 3 rodadas prévias), o que eleva ligeiramente os tempos e a variância. Com entradas maiores, o laço principal está completamente compilado para código de máquina nativo, e a razão se estabiliza.

A diferença entre as linguagens reflete a natureza dos *runtimes*: o **CPython** executa o algoritmo por interpretação de *bytecodes* (cada operação envolve despacho dinâmico e verificações de tipo em tempo de execução), enquanto o **Node.js (V8)** compila o código JavaScript para código de máquina com otimizações agressivas via JIT (*Just-In-Time compilation*) — incluindo *inline caching*, eliminação de verificações de tipo e vetorização dos laços internos.

É fundamental observar que, apesar das diferenças absolutas de tempo, **ambas as implementações exibem a mesma curva assintótica**: o crescimento relativo entre os tamanhos é idêntico nas duas linguagens, confirmando que a complexidade é uma propriedade do algoritmo, não do ambiente de execução.

### 4.3 Trabalho algorítmico: nós expandidos

**Figura 7 – Nós expandidos por cenário**

![Nós expandidos](../results/graficos/nos_expandidos.png)

Fonte: elaborado pelos autores (2026).

Este gráfico é único em relação aos anteriores: em vez de medir tempo de CPU (que varia entre linguagens e máquinas), ele mede o **trabalho algorítmico puro** — o número de nós expandidos pelo A\* em cada cenário. Como as duas implementações expandem exatamente os mesmos nós (verificado pelo script de equivalência), os valores são idênticos entre Python e JavaScript e a série é única por cenário.

Os três cenários mostram crescimentos claramente distintos com n:

- **Melhor caso:** crescimento proporcional a √n (51, 151, 301 nós para n = 2.601, 22.801 e 90.601). A heurística de Manhattan é perfeita para o caminho reto, e o A\* não expande nenhum vértice além do necessário.

- **Caso médio:** crescimento aproximadamente linear (~251, ~1.768, ~6.756 nós, representando ~8–9% de n). A fração constante expandida reflete que, com obstáculos aleatórios de densidade 25%, a heurística orienta a busca de forma consistente, explorando apenas uma porção quase constante da grade.

- **Pior caso:** crescimento proporcional a n/2 (1.301, 11.401, 45.601 nós, representando ~50% de n). No labirinto em serpentina, o algoritmo é obrigado a percorrer todos os vértices do único caminho possível, sem poder podar nenhum.

Este gráfico demonstra com clareza que o cenário — determinado pela estrutura da entrada e pela qualidade da heurística — é o principal determinante do desempenho do A\*, muito mais do que o tamanho absoluto da grade.

### 4.4 Validação do modelo teórico

A comparação entre os tempos medidos e as curvas teóricas normalizadas (linhas tracejadas nas Figuras 1, 2 e 3) demonstra boa aderência do comportamento empírico às previsões da análise assintótica:

- No **pior caso**, as medições de Python e JavaScript seguem a curva n log n ao longo de quase dois fatores de 10 em n, com pequenos desvios que ficam dentro das barras de erro. A constante multiplicativa empírica — razão entre o tempo medido e o valor n log n — é estável para todos os tamanhos, confirmando Θ(n log n).

- No **caso médio**, os pontos seguem a reta de inclinação 1 (função linear) em escala log-log, com variância maior devida à heterogeneidade das instâncias. A fração constante de ~8% de nós expandidos sustenta a classificação empírica ≈ Θ(n).

- No **melhor caso**, o Python segue a curva √n de forma clara; o JavaScript mostra comportamento dominado por overhead fixo para n pequeno, convergindo para √n apenas nas entradas maiores. Esse desvio prático não invalida a análise teórica — ele ressalta que a análise assintótica descreve o crescimento para n suficientemente grande, e que constantes ocultas e custos fixos de *runtime* podem dominar em entradas pequenas.

---

## 5 APLICABILIDADE: EFICIÊNCIA E LIMITAÇÕES

### 5.1 Contextos de eficiência e aplicações

O A\* é o algoritmo de *pathfinding* mais amplamente utilizado em contextos onde: (a) existe um único par origem-destino por consulta, (b) os pesos das arestas são não negativos e (c) está disponível uma heurística admissível barata de calcular. Nessas condições, o A\* supera o Dijkstra ao explorar muito menos vértices — como demonstrado neste trabalho, o melhor caso expande apenas √n vértices, enquanto o Dijkstra exploraria toda a grade (n vértices).

Entre os principais contextos de aplicação estão:

- **Jogos e motores de jogo:** *pathfinding* de unidades em mapas em grade (estratégia em tempo real, RPGs) e em malhas de navegação (*navmesh*), que é a generalização do A\* para superfícies 3D irregulares. O A\* é o algoritmo padrão de bibliotecas como Recast/Detour (usada em Unity e Unreal Engine).

- **Robótica e veículos autônomos:** planejamento de rota em mapas de ocupação 2D ou 3D. A heurística euclideana (ou Manhattan para grades discretizadas) guia o robô de forma eficiente mesmo em ambientes com muitos obstáculos.

- **Navegação e GPS:** variantes do A\* com heurísticas geográficas (distância em linha reta entre coordenadas) são a base de sistemas como o algoritmo ALT (*A\* with Landmarks and Triangle inequality*) e das hierarquias de contração, que pré-processam grafos de rodovias para consultas de sub-milissegundo.

- **Planejamento automático (IA clássica):** resolução de *puzzles* como o 15-puzzle e o cubo mágico, usando heurísticas de padrão (*pattern databases*). O A\* com essas heurísticas é o método ótimo de referência para benchmarks de planejamento.

- **Redes e telecomunicações:** roteamento em grafos de rede com estimativas de latência como heurística.

O algoritmo é especialmente eficiente quando a heurística é informativa (próxima do custo real), o grafo é esparso (baixa densidade de obstáculos) e o destino é único por consulta. Nessas condições, a prática confirma o comportamento do melhor e do caso médio: poucos vértices são explorados, e o tempo de execução é muito inferior ao custo do Dijkstra.

### 5.2 Limitações

Apesar da ampla aplicabilidade, o A\* possui limitações relevantes:

- **Memória O(n):** o A\* mantém em memória todos os vértices descobertos (g-scores, pais e heap). Em espaços de estados muito grandes — como o espaço de configurações do 15-puzzle (≈ 10¹³ estados) ou de planejamento de tarefas — a fronteira pode crescer exponencialmente até esgotar a memória. Variantes como IDA\* (busca iterativa por aprofundamento), SMA\* e *fringe search* trocam memória por recomputação, tornando-se mais adequadas nesses casos.

- **Qualidade da heurística:** o desempenho do A\* depende criticamente da precisão de h. Se a heurística for fraca (h ≡ 0, por exemplo), o algoritmo degenera para Dijkstra, explorando n vértices mesmo que o destino esteja próximo — como observado no pior caso deste trabalho. Por outro lado, heurísticas inadmissíveis (que superestimam o custo) aceleram a busca mas perdem a garantia de otimalidade; variantes como *Weighted A\** exploram esse *trade-off* deliberadamente.

- **Ambientes dinâmicos:** em mapas que mudam durante a execução (obstáculos móveis, custos variáveis), o A\* precisa ser executado do zero a cada mudança. Algoritmos como D\* e D\* Lite foram desenvolvidos especificamente para replanejamento incremental eficiente.

- **Pesos negativos:** assim como o Dijkstra, o A\* não funciona corretamente com arestas de peso negativo. O Bellman-Ford, com complexidade O(V·E), é a alternativa para esses casos.

- **Múltiplas consultas:** quando são necessários caminhos entre muitos pares origem-destino no mesmo grafo, técnicas de pré-processamento como *contraction hierarchies* ou TRANSIT superam o A\* puro por ordens de grandeza, ao armazenar atalhos pré-computados.

Em resumo, o A\* é altamente eficiente para o cenário de consulta única em grafo estático com boa heurística, mas existem situações — espaços de estados imensos, ambientes dinâmicos ou múltiplas consultas — em que outras abordagens são preferíveis.

---

## 6 REFLEXÃO TEÓRICA: CLASSES DE COMPLEXIDADE

Esta seção relaciona o algoritmo estudado com as classes de complexidade computacional, em especial as classes P e NP, e discute a existência de problemas correlatos de difícil solução.

### 6.1 O problema pertence à classe P?

Sim. A classe P é composta pelos problemas de decisão que podem ser resolvidos por um algoritmo determinístico em tempo polinomial em relação ao tamanho da entrada. O problema do **caminho mínimo entre dois vértices** — na versão de decisão "existe caminho de custo ≤ k?" — é resolvido pelo A\* em tempo O(n log n), que é polinomial em n (número de células). Portanto, o problema pertence à classe P: existe um algoritmo eficiente e exato que o resolve em tempo polinomial.

Uma consequência direta é que o problema também pertence à classe NP, já que P ⊆ NP. Em termos práticos, isso significa que para qualquer caminho proposto como solução, basta percorrê-lo uma vez (em tempo O(n)) para verificar se o custo é ≤ k — verificação polinomial e fácil.

### 6.2 Existe uma versão NP do problema?

O problema do caminho mínimo, na sua forma usual, não é NP-difícil. Contudo, variações aparentemente pequenas no enunciado podem elevar drasticamente a dificuldade:

- **Caminho simples mais longo (*longest path*):** encontrar o caminho simples de maior custo entre dois vértices é NP-difícil. A diferença em relação ao caminho mínimo é apenas trocar "menor" por "maior", mas isso elimina a propriedade subestrutura ótima (princípio da otimalidade) que torna o caminho mínimo solúvel em tempo polinomial.

- **Caminho mínimo com restrições de recursos (RCSP):** o problema do caminho mínimo com restrição de recursos — "encontrar o caminho de menor custo sujeito a não exceder um orçamento de algum outro recurso (tempo, combustível, etc.)" — é NP-difícil. Mesmo com pesos não negativos, a presença de restrições adicionais quebra a estrutura polinomial.

- **Planejamento multiagente ótimo (*Multi-Agent Pathfinding*, MAPF):** encontrar caminhos de custo total mínimo para múltiplos agentes em um grafo compartilhado, sem colisões, é NP-difícil. O A\* pode ser adaptado para MAPF (CBS — *Conflict-Based Search*), mas o problema em geral não admite solução polinomial.

- **Problema do (n²−1)-*puzzle* ótimo:** a generalização do 15-puzzle para n² − 1 peças é NP-difícil (Ratner e Warmuth, 1990). O A\* continua correto e ótimo nesses espaços de estados, mas o número de estados é exponencial em n — o algoritmo roda em tempo exponencial. Ser ótimo não implica ser polinomial quando o espaço de estados é exponencial.

A fronteira entre tratável e intratável é, portanto, tênue: o caminho mínimo em grafos explícitos está em P, mas bastam restrições adicionais, a troca do critério de otimização ou a exponencialidade do espaço de estados para a classe mudar.

### 6.3 Problemas semelhantes NP-completos

Existem problemas de grafos que se assemelham superficialmente ao caminho mínimo — minimizar custo em um grafo — mas são NP-completos (na forma de decisão) ou NP-difíceis (na forma de otimização):

- **Problema do Caixeiro-Viajante (*Travelling Salesman Problem*, TSP):** encontrar o ciclo de menor custo que visita todos os vértices exatamente uma vez. A versão de decisão ("existe tal ciclo com custo ≤ k?") é NP-completa. A diferença fundamental em relação ao caminho mínimo é a restrição de visitação: no TSP, o caminho deve ser hamiltoniano, enquanto no caminho mínimo não há restrição de quais vértices visitar.

- **Caminho Hamiltoniano:** determinar se existe um caminho simples que passa por todos os vértices exatamente uma vez é NP-completo. O TSP com grafo completo é uma generalização ponderada deste problema.

- **Caminho mínimo entre múltiplos pares com orçamento compartilhado:** variantes em que n agentes precisam encontrar caminhos mínimos e o custo total não pode exceder um orçamento são NP-difíceis — evidência de que a versão multiagente é qualitativamente mais difícil.

A comparação é instrutiva: enquanto o caminho mínimo resolvido pelo A\* está em P e escala bem (confirmado pelos experimentos com até 90.601 células em menos de 100 ms), o TSP e o caminho hamiltoniano não possuem, até hoje, algoritmo de tempo polinomial conhecido. Caso fosse descoberto tal algoritmo para qualquer problema NP-completo, ter-se-ia P = NP — uma das maiores questões em aberto da Ciência da Computação. O fato de o A\* pertencer à classe P é, portanto, uma vantagem teórica expressiva: garante eficiência comprovada e escalabilidade, ao contrário dos problemas NP-completos correlatos.

---

## 7 EXECUÇÃO DO PROJETO

Esta seção descreve como reproduzir todo o experimento a partir do código-fonte. O repositório está disponível em:

**https://github.com/P4d1lh4/Projeto-Teoria-A-**

A estrutura de pastas do projeto é a seguinte:

```
python/         código + benchmark em Python
javascript/     código + benchmark em JavaScript (Node.js)
tools/          script de verificação de equivalência
results/        CSVs e gráficos gerados pelos experimentos
docs/           relatório, slides e tabelas
demo/           demonstração visual interativa (index.html)
```

### 7.1 Pré-requisitos

É necessário ter **Python 3.10+** e **Node.js 18+** instalados. A única dependência de análise em Python é o `matplotlib`:

```bash
pip install matplotlib
```

### 7.2 Executando os testes

```bash
# Testes unitários em Python
python -m unittest discover -s python -v

# Testes em JavaScript
node --test javascript/test/astar.test.js

# Verificação de equivalência entre as linguagens
python tools/verificar_equivalencia.py
```

### 7.3 Executando os benchmarks

Os benchmarks executam o algoritmo 30 vezes em cada combinação de cenário e tamanho (após 3 rodadas de aquecimento) e salvam os resultados em CSVs:

```bash
# Benchmark em Python  (gera results/resultados_python.csv)
python python/benchmark.py

# Benchmark em JavaScript  (gera results/resultados_javascript.csv)
node javascript/benchmark.js

# Versão rápida para teste (5 rodadas, apenas tamanhos nomeados)
python python/benchmark.py --rapido
```

### 7.4 Gerando os gráficos e tabelas

Após executar ambos os benchmarks, os gráficos e as tabelas são gerados com um único comando:

```bash
python python/charts.py
```

O comando produz os arquivos em `results/graficos/` (gráficos PNG) e `docs/tabelas_resultados.md` (tabelas em Markdown).

### 7.5 Demonstração visual

Abrir o arquivo `demo/index.html` em qualquer navegador moderno exibe o A\* explorando a grade em tempo real, com visualização das células abertas, fechadas e do caminho encontrado. A demonstração é útil para a apresentação oral.

---

## 8 CONCLUSÃO

Este trabalho apresentou um estudo teórico e experimental do algoritmo A\* para o problema do caminho mínimo em grades 2D com obstáculos. Do ponto de vista teórico, mostrou-se que o algoritmo, implementado com heap binário de mínimo e heurística de Manhattan admissível e consistente, é ótimo (retorna sempre o caminho de menor custo), possui limite superior de tempo O(n log n), limite inferior Ω(√n · log n) para o melhor caso e não admite um limite Θ global — pois o comportamento assintótico varia substancialmente com a qualidade da heurística e a estrutura da entrada. Por ter solução em tempo polinomial, o problema pertence à classe P, ao contrário de variantes correlatas como o Caixeiro-Viajante e o caminho hamiltoniano, que são NP-completos.

Os experimentos confirmaram com precisão as previsões teóricas. No **pior caso** (labirinto em serpentina), os tempos crescem como n log n — evidenciado pela aderência das curvas em escala log-log — e ~50% das células são expandidas, demonstrando que a heurística não consegue podar nenhuma região da busca. No **caso médio** (obstáculos aleatórios 25%), o crescimento é aproximadamente linear e a fração de células expandidas (~8%) permanece constante entre os tamanhos, confirmando a eficácia da heurística em instâncias realistas. No **melhor caso** (grade vazia, caminho reto), o A\* expande exatamente √n vértices — confirmado pela contagem exata de nós —, e o tempo no Python segue a curva √n, enquanto no JavaScript o custo fixo do *runtime* domina para entradas pequenas.

Na comparação entre linguagens, o JavaScript executado no Node.js mostrou-se consistentemente mais rápido que o Python, com vantagem de 4,5 a 6,4 vezes no pior caso, graças às otimizações do compilador JIT do motor V8. O Python, por sua vez, apresentou medições mais estáveis (menor variância) nos cenários determinísticos e mostrou-se mais eficiente para entradas muito pequenas no melhor caso, onde o custo fixo do V8 supera o ganho do JIT. Ambas as implementações, contudo, exibiram o mesmo padrão de crescimento assintótico, o que reforça que a complexidade é uma propriedade do algoritmo, e não da linguagem.

Uma contribuição metodológica relevante deste trabalho foi a verificação formal de equivalência entre as implementações: ao usar o mesmo PRNG reproduzido bit a bit, os mesmos critérios de desempate no heap e um script de verificação automática, garantiu-se que as duas linguagens processam exatamente as mesmas entradas e expandem exatamente os mesmos nós — tornando a comparação de tempos uma medição pura do desempenho de cada *runtime*, sem interferência de diferenças algorítmicas.

---

## REFERÊNCIAS

HART, P. E.; NILSSON, N. J.; RAPHAEL, B. A formal basis for the heuristic determination of minimum cost paths. **IEEE Transactions on Systems Science and Cybernetics**, v. 4, n. 2, p. 100–107, 1968.

RUSSELL, S.; NORVIG, P. **Artificial Intelligence: A Modern Approach**. 4. ed. Hoboken: Pearson, 2020. (Capítulo 3 — busca informada e exploração)

CORMEN, T. H. et al. **Introduction to Algorithms**. 4. ed. Cambridge: MIT Press, 2022. (Capítulo 22 — Dijkstra e filas de prioridade)

RATNER, D.; WARMUTH, M. The (n²−1)-puzzle and related relocation problems. **Journal of Symbolic Computation**, v. 10, n. 2, p. 111–137, 1990.

GAREY, M. R.; JOHNSON, D. S. **Computers and Intractability: A Guide to the Theory of NP-Completeness**. New York: W. H. Freeman, 1979.

ZIVIANI, N. **Projeto de Algoritmos com Implementações em Java e C++**. São Paulo: Cengage Learning, 2007.
