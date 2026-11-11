"""Verifica que TODAS las citas «...» de un cuestionario aparezcan literalmente en el texto del libro.

Uso:
    python -I scripts/verificar_citas.py cuestionario.md md/libro_completo.md

Sale con código 1 y lista las citas que no encuentra (posibles errores o invenciones).
La comparación ignora diferencias de espacios/saltos de línea y un "…" final de la cita.
Las citas que no son del libro (p. ej. títulos o palabras sueltas) se pueden excluir
escribiéndolas con comillas normales "..." en vez de «...».
"""
import re
import sys


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola Windows: python -I ignora PYTHONIOENCODING
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    quiz = open(sys.argv[1], encoding="utf-8").read()
    book = norm(open(sys.argv[2], encoding="utf-8").read().replace("\\*", "*"))
    quotes = [norm(q).rstrip("…").strip() for q in re.findall(r"«([^»]+)»", quiz)]
    missing = sorted({q for q in quotes if q and q not in book})
    print(f"Citas revisadas: {len(quotes)} · no encontradas: {len(missing)}")
    for q in missing:
        print("  ✗", q)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
