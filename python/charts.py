"""Gera os gráficos e tabelas a partir dos CSVs de resultados.

Requisito da especificação: eixo X = tamanho da entrada (n), eixo Y = tempo,
com a curva da complexidade TEÓRICA sobreposta aos dados medidos e escalas
logarítmicas quando necessário.

Entradas:  results/resultados_python.csv, results/resultados_javascript.csv
Saídas:    results/graficos/*.png
           results/resumo.csv               (média e desvio-padrão agregados)
           docs/tabelas_resultados.md       (tabelas prontas para o relatório)

Curvas teóricas usadas (normalizadas pelo maior ponto medido de cada série):
- melhor caso:  c * sqrt(n)      — o A* expande só o caminho reto (lado = sqrt(n))
- caso médio:   c * n            — fração constante da grade explorada
- pior caso:    c * n log2(n)    — quase todas as células passam pelo heap

Uso (da raiz do repositório, após rodar os dois benchmarks):
    python python/charts.py
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
DIR_RESULTADOS = RAIZ / "results"
DIR_GRAFICOS = DIR_RESULTADOS / "graficos"
ARQUIVO_RESUMO = DIR_RESULTADOS / "resumo.csv"
ARQUIVO_TABELAS = RAIZ / "docs" / "tabelas_resultados.md"

CENARIOS = ("melhor", "medio", "pior")
NOME_CENARIO = {"melhor": "Melhor caso", "medio": "Caso médio", "pior": "Pior caso"}
COR = {"python": "#306998", "javascript": "#b8860b"}
NOME_LINGUAGEM = {"python": "Python", "javascript": "JavaScript"}

TEORIA = {
    "melhor": (lambda n: math.sqrt(n), "Θ(√n)"),
    "medio": (lambda n: n, "~Θ(n)"),
    "pior": (lambda n: n * math.log2(n), "Θ(n log n)"),
}


def carregar() -> list[dict]:
    medicoes = []
    for linguagem in ("python", "javascript"):
        caminho = DIR_RESULTADOS / f"resultados_{linguagem}.csv"
        if not caminho.exists():
            raise SystemExit(
                f"Arquivo {caminho} não encontrado. Rode os benchmarks antes:\n"
                "  python python/benchmark.py\n  node javascript/benchmark.js")
        with open(caminho, newline="", encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                medicoes.append({
                    "linguagem": linha["linguagem"],
                    "cenario": linha["cenario"],
                    "rotulo": linha["rotulo"],
                    "lado": int(linha["lado"]),
                    "n": int(linha["n_celulas"]),
                    "tempo_ms": float(linha["tempo_ms"]),
                    "expandidos": int(linha["nos_expandidos"]),
                    "custo": float(linha["custo_caminho"]),
                })
    return medicoes


def agregar(medicoes):
    """Agrupa por (linguagem, cenario, lado) -> estatísticas."""
    grupos = defaultdict(list)
    for m in medicoes:
        grupos[(m["linguagem"], m["cenario"], m["lado"])].append(m)

    agregados = {}
    for chave, grupo in grupos.items():
        tempos = [m["tempo_ms"] for m in grupo]
        agregados[chave] = {
            "rotulo": grupo[0]["rotulo"],
            "n": grupo[0]["n"],
            "rodadas": len(tempos),
            "media_ms": statistics.mean(tempos),
            "desvio_ms": statistics.stdev(tempos) if len(tempos) > 1 else 0.0,
            "expandidos_media": statistics.mean(m["expandidos"] for m in grupo),
            "custo_medio": statistics.mean(m["custo"] for m in grupo),
        }
    return agregados


def serie(agregados, linguagem, cenario):
    """Pontos (n, média, desvio) ordenados por n para uma série."""
    chaves = sorted(k for k in agregados if k[0] == linguagem and k[1] == cenario)
    ns = [agregados[k]["n"] for k in chaves]
    medias = [agregados[k]["media_ms"] for k in chaves]
    desvios = [agregados[k]["desvio_ms"] for k in chaves]
    return ns, medias, desvios


def grafico_aderencia(agregados, cenario):
    """Tempos medidos (Py e JS) + curva teórica normalizada, escala log-log."""
    fig, ax = plt.subplots(figsize=(8, 5))
    funcao, nome_teoria = TEORIA[cenario]

    for linguagem in ("python", "javascript"):
        ns, medias, desvios = serie(agregados, linguagem, cenario)
        ax.errorbar(ns, medias, yerr=desvios, marker="o", capsize=3,
                    color=COR[linguagem], label=f"{NOME_LINGUAGEM[linguagem]} (medido)")
        # Normaliza a teoria pelo último ponto medido da própria série.
        c = medias[-1] / funcao(ns[-1])
        teoricos = [c * funcao(n) for n in ns]
        ax.plot(ns, teoricos, "--", color=COR[linguagem], alpha=0.6,
                label=f"{NOME_LINGUAGEM[linguagem]}: teoria {nome_teoria}")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n = células da grade (escala log)")
    ax.set_ylabel("tempo médio (ms, escala log)")
    ax.set_title(f"A* — {NOME_CENARIO[cenario]}: medições × complexidade teórica")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / f"aderencia_{cenario}.png", dpi=150)
    plt.close(fig)


def grafico_cenarios_por_linguagem(agregados, linguagem):
    """As três curvas (melhor/médio/pior) de uma linguagem, log-log."""
    fig, ax = plt.subplots(figsize=(8, 5))
    estilo = {"melhor": "tab:green", "medio": "tab:blue", "pior": "tab:red"}
    for cenario in CENARIOS:
        ns, medias, desvios = serie(agregados, linguagem, cenario)
        ax.errorbar(ns, medias, yerr=desvios, marker="o", capsize=3,
                    color=estilo[cenario], label=NOME_CENARIO[cenario])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n = células da grade (escala log)")
    ax.set_ylabel("tempo médio (ms, escala log)")
    ax.set_title(f"A* em {NOME_LINGUAGEM[linguagem]} — análise de casos")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / f"casos_{linguagem}.png", dpi=150)
    plt.close(fig)


def grafico_comparacao_linguagens(agregados):
    """Barras: Python × JavaScript no pior caso, tamanhos nomeados."""
    nomeados = [(k, v) for k, v in agregados.items()
                if k[1] == "pior" and v["rotulo"] != "intermediaria"]
    lados = sorted({k[2] for k, _ in nomeados})
    rotulos = {}
    for (linguagem, _, lado), v in nomeados:
        rotulos[lado] = v["rotulo"]

    fig, ax = plt.subplots(figsize=(8, 5))
    largura = 0.35
    posicoes = range(len(lados))
    for deslocamento, linguagem in ((-largura / 2, "python"), (largura / 2, "javascript")):
        medias = [agregados[(linguagem, "pior", lado)]["media_ms"] for lado in lados]
        desvios = [agregados[(linguagem, "pior", lado)]["desvio_ms"] for lado in lados]
        barras = ax.bar([p + deslocamento for p in posicoes], medias, largura,
                        yerr=desvios, capsize=4, color=COR[linguagem],
                        label=NOME_LINGUAGEM[linguagem])
        ax.bar_label(barras, fmt="%.1f", padding=2, fontsize=8)
    ax.set_xticks(list(posicoes))
    ax.set_xticklabels([f"{rotulos[lado]}\n{lado}×{lado}" for lado in lados])
    ax.set_ylabel("tempo médio (ms)")
    rodadas = agregados[("python", "pior", lados[0])]["rodadas"]
    ax.set_title(f"Pior caso — comparação entre linguagens (média de {rodadas} rodadas)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "comparacao_linguagens.png", dpi=150)
    plt.close(fig)


def grafico_nos_expandidos(agregados):
    """Nós expandidos × n (idênticos nas duas linguagens, por construção)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    estilo = {"melhor": "tab:green", "medio": "tab:blue", "pior": "tab:red"}
    for cenario in CENARIOS:
        chaves = sorted(k for k in agregados if k[0] == "python" and k[1] == cenario)
        ns = [agregados[k]["n"] for k in chaves]
        expandidos = [agregados[k]["expandidos_media"] for k in chaves]
        ax.plot(ns, expandidos, marker="o", color=estilo[cenario],
                label=NOME_CENARIO[cenario])
    ax.plot([0], [0], alpha=0)  # ancora origem visualmente
    ax.set_xlabel("n = células da grade")
    ax.set_ylabel("nós expandidos (média)")
    ax.set_title("Trabalho algorítmico: nós expandidos por cenário\n"
                 "(idêntico em Python e JavaScript — mesma entrada, mesmo desempate)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "nos_expandidos.png", dpi=150)
    plt.close(fig)


def validar_equivalencia(agregados) -> list[str]:
    """Confere que nós expandidos e custos são idênticos entre as linguagens
    (melhor/pior; no caso médio compara as médias das mesmas 30 grades)."""
    avisos = []
    for cenario in CENARIOS:
        for chave_py in sorted(k for k in agregados if k[0] == "python" and k[1] == cenario):
            chave_js = ("javascript", chave_py[1], chave_py[2])
            if chave_js not in agregados:
                avisos.append(f"sem dados JS para {chave_py}")
                continue
            py, js = agregados[chave_py], agregados[chave_js]
            if py["expandidos_media"] != js["expandidos_media"] or \
                    py["custo_medio"] != js["custo_medio"]:
                avisos.append(
                    f"DIVERGÊNCIA em {cenario} lado={chave_py[2]}: "
                    f"expandidos py={py['expandidos_media']} js={js['expandidos_media']}, "
                    f"custo py={py['custo_medio']} js={js['custo_medio']}")
    return avisos


def escrever_resumo(agregados):
    with open(ARQUIVO_RESUMO, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["linguagem", "cenario", "rotulo", "lado", "n_celulas",
                           "rodadas", "tempo_medio_ms", "desvio_padrao_ms",
                           "nos_expandidos_media", "custo_medio"])
        for chave in sorted(agregados):
            v = agregados[chave]
            escritor.writerow([
                chave[0], chave[1], v["rotulo"], chave[2], v["n"], v["rodadas"],
                f"{v['media_ms']:.6f}", f"{v['desvio_ms']:.6f}",
                f"{v['expandidos_media']:.1f}", f"{v['custo_medio']:.1f}",
            ])


def escrever_tabelas(agregados):
    """Tabelas em Markdown (tamanhos nomeados) para colar no relatório."""
    linhas = ["# Tabelas de resultados",
              "",
              "Geradas automaticamente por `python python/charts.py` a partir de",
              "`results/resultados_python.csv` e `results/resultados_javascript.csv`",
              "(média ± desvio-padrão de 30 rodadas por célula da tabela).",
              ""]
    for cenario in CENARIOS:
        linhas.append(f"## {NOME_CENARIO[cenario]}")
        linhas.append("")
        linhas.append("| Tamanho | Grade | n (células) | Nós expandidos | Custo do caminho | "
                      "Python (ms) | JavaScript (ms) | Python/JS |")
        linhas.append("|---|---|---|---|---|---|---|---|")
        chaves = sorted(
            (k for k in agregados
             if k[0] == "python" and k[1] == cenario
             and agregados[k]["rotulo"] != "intermediaria"),
            key=lambda k: k[2])
        for chave_py in chaves:
            v_py = agregados[chave_py]
            v_js = agregados[("javascript", cenario, chave_py[2])]
            razao = v_py["media_ms"] / v_js["media_ms"] if v_js["media_ms"] else float("nan")
            linhas.append(
                f"| {v_py['rotulo']} | {chave_py[2]}×{chave_py[2]} | {v_py['n']} "
                f"| {v_py['expandidos_media']:.0f} | {v_py['custo_medio']:.0f} "
                f"| {v_py['media_ms']:.3f} ± {v_py['desvio_ms']:.3f} "
                f"| {v_js['media_ms']:.3f} ± {v_js['desvio_ms']:.3f} "
                f"| {razao:.1f}× |")
        linhas.append("")
    ARQUIVO_TABELAS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_TABELAS.write_text("\n".join(linhas), encoding="utf-8")


def main():
    medicoes = carregar()
    agregados = agregar(medicoes)

    avisos = validar_equivalencia(agregados)
    if avisos:
        for aviso in avisos:
            print(f"AVISO: {aviso}")
    else:
        print("Equivalência confirmada: nós expandidos e custos idênticos entre linguagens.")

    DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)
    for cenario in CENARIOS:
        grafico_aderencia(agregados, cenario)
    for linguagem in ("python", "javascript"):
        grafico_cenarios_por_linguagem(agregados, linguagem)
    grafico_comparacao_linguagens(agregados)
    grafico_nos_expandidos(agregados)
    escrever_resumo(agregados)
    escrever_tabelas(agregados)

    print(f"Gráficos em {DIR_GRAFICOS}")
    print(f"Resumo em {ARQUIVO_RESUMO}")
    print(f"Tabelas em {ARQUIVO_TABELAS}")


if __name__ == "__main__":
    main()
