# Tabelas de resultados

Geradas automaticamente por `python python/charts.py` a partir de
`results/resultados_python.csv` e `results/resultados_javascript.csv`
(média ± desvio-padrão de 30 rodadas por célula da tabela).

## Melhor caso

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 51 | 50 | 0.166 ± 0.004 | 0.261 ± 0.205 | 0.6× |
| media | 151×151 | 22801 | 151 | 150 | 0.704 ± 0.212 | 0.379 ± 0.115 | 1.9× |
| grande | 301×301 | 90601 | 301 | 300 | 1.149 ± 0.051 | 0.338 ± 0.067 | 3.4× |

## Caso médio

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 251 | 100 | 0.669 ± 0.203 | 0.488 ± 0.168 | 1.4× |
| media | 151×151 | 22801 | 1768 | 300 | 5.383 ± 5.982 | 1.499 ± 1.943 | 3.6× |
| grande | 301×301 | 90601 | 6756 | 601 | 22.101 ± 19.169 | 9.693 ± 6.448 | 2.3× |

## Pior caso

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 1301 | 1300 | 2.235 ± 0.181 | 0.351 ± 0.105 | 6.4× |
| media | 151×151 | 22801 | 11401 | 11400 | 21.556 ± 0.618 | 4.292 ± 0.543 | 5.0× |
| grande | 301×301 | 90601 | 45601 | 45600 | 94.109 ± 2.263 | 20.874 ± 3.672 | 4.5× |
