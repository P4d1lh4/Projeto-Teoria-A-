"""Verifica que as implementações Python e JavaScript são equivalentes.

Executa `python python/scenarios.py --check` e `node javascript/scenarios.js
--check` e exige saídas IDÊNTICAS: mesmos valores do PRNG, mesmos hashes de
grade (FNV-1a), mesmos custos de caminho e mesmo número de nós expandidos.

Isso garante que os benchmarks das duas linguagens medem exatamente o mesmo
trabalho algorítmico sobre exatamente as mesmas entradas.

Uso (da raiz do repositório):
    python tools/verificar_equivalencia.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def rodar(comando: list[str]) -> str:
    resultado = subprocess.run(
        comando, cwd=RAIZ, capture_output=True, text=True, check=True,
    )
    return resultado.stdout.replace("\r\n", "\n").strip()


def main() -> int:
    saida_py = rodar([sys.executable, str(RAIZ / "python" / "scenarios.py"), "--check"])
    saida_js = rodar(["node", str(RAIZ / "javascript" / "scenarios.js"), "--check"])

    if saida_py == saida_js:
        print("OK: as duas implementações são equivalentes.")
        print()
        print("Saída verificada (PRNG | cenário, lado, [seed,] hash, custo, expandidos):")
        print(saida_py)
        return 0

    print("ERRO: as saídas divergem!", file=sys.stderr)
    linhas_py = saida_py.splitlines()
    linhas_js = saida_js.splitlines()
    for i in range(max(len(linhas_py), len(linhas_js))):
        py = linhas_py[i] if i < len(linhas_py) else "<ausente>"
        js = linhas_js[i] if i < len(linhas_js) else "<ausente>"
        marca = "  " if py == js else "!!"
        print(f"{marca} python: {py}", file=sys.stderr)
        if py != js:
            print(f"{marca} js:     {js}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
