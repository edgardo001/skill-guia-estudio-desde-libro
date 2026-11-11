"""Une md/hoja_*.md (OCR) o md/parte_*.md (extraer_libro.py) en md/libro_completo.md con una cabecera.

Uso:
    python -I scripts/unir_libro.py md "Título" "Autor" "Colección/editorial" "I. Cuento 1 (págs. 9-40)" "II. …"

Los argumentos después del tercero son la lista de cuentos o capítulos con su rango de páginas
del libro impreso (opcional). Se vuelve a ejecutar cada vez que se corrige una hoja.
"""
import sys
from pathlib import Path


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola Windows: python -I ignora PYTHONIOENCODING
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    folder, title, author, publisher, *parts = sys.argv[1:]
    folder = Path(folder)
    sheets = sorted(folder.glob("hoja_*.md")) + sorted(folder.glob("parte_*.md"))
    if not sheets:
        sys.exit(f"No hay archivos hoja_*.md ni parte_*.md en {folder}")
    head = [f"# {title} — texto completo", "", f"Autor: {author}. {publisher}.", ""]
    if parts:
        head += ["Contenido: " + " · ".join(parts) + ".", ""]
    body = "\n".join(s.read_text(encoding="utf-8").rstrip() + "\n" for s in sheets)
    out = folder / "libro_completo.md"
    out.write_text("\n".join(head) + "\n" + body, encoding="utf-8")
    print(f"{out}: {len(sheets)} archivos, {len(body.split())} palabras")


if __name__ == "__main__":
    main()
