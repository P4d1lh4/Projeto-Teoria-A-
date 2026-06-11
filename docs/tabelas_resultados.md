# Tabelas de resultados

Geradas automaticamente por `python python/charts.py` a partir de
`results/resultados_python.csv` e `results/resultados_javascript.csv`
(média ± desvio-padrão de 30 rodadas por célula da tabela).

## Melhor caso

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 51 | 50 | 0.164 ± 0.004 | 0.570 ± 0.295 | 0.3× |
| media | 151×151 | 22801 | 151 | 150 | 0.521 ± 0.003 | 0.640 ± 0.150 | 0.8× |
| grande | 301×301 | 90601 | 301 | 300 | 1.157 ± 0.045 | 0.762 ± 0.186 | 1.5× |

## Caso médio

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 288 | 100 | 0.728 ± 0.182 | 0.465 ± 0.091 | 1.6× |
| media | 151×151 | 22801 | 1343 | 300 | 3.857 ± 1.139 | 1.529 ± 1.291 | 2.5× |
| grande | 301×301 | 90601 | 5623 | 602 | 17.895 ± 11.511 | 8.530 ± 6.017 | 2.1× |

## Pior caso

| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | Python (ms) | JavaScript (ms) | Python/JS |
|---|---|---|---|---|---|---|---|
| pequena | 51×51 | 2601 | 1301 | 1300 | 2.254 ± 0.050 | 0.369 ± 0.053 | 6.1× |
| media | 151×151 | 22801 | 11401 | 11400 | 22.083 ± 0.535 | 4.705 ± 0.463 | 4.7× |
| grande | 301×301 | 90601 | 45601 | 45600 | 91.816 ± 2.066 | 22.920 ± 2.995 | 4.0× |
