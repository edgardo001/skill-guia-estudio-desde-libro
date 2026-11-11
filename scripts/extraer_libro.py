"""Extrae el texto de un libro en cualquier formato a archivos Markdown (md/parte_NNN.md).

Uso:
    python -I extraer_libro.py LIBRO.ext CARPETA_SALIDA [--primera-pagina N]

Formatos:
    .pdf con texto      -> una parte por página del PDF, con "## Página X"
                           (--primera-pagina = número impreso de la página 1 del PDF, si se conoce;
                            si no, se usa la etiqueta de página del PDF o su número de orden)
    .pdf escaneado      -> se detecta y se indica usar ocr_pdf.py (imágenes -> OCR)
    .epub               -> una parte por capítulo (orden del índice/spine), con "## Capítulo N: título"
    .docx               -> una parte por título de nivel 1 (o una sola parte si no hay títulos)
    .txt / .md          -> una sola parte (los capítulos se detectan después a mano)
    .html / .htm        -> una sola parte
    otros (.odt .rtf .doc .mobi .fb2 .azw3 …) -> pandoc (si está instalado) o PyMuPDF

Libros sin páginas (EPUB, DOCX, TXT, HTML…): las respuestas de la guía citan el capítulo
"(cap. N)" en vez de la página. Ver SKILL.md.

Requisitos: pip install pymupdf  (lo demás usa solo la biblioteca estándar; pandoc es opcional)
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


# ---------------------------------------------------------------- utilidades
class HTML2MD(HTMLParser):
    """Convierte HTML/XHTML simple a Markdown: títulos, párrafos, listas, negrita y cursiva."""
    BLOCK = {"p", "div", "li", "br", "tr", "blockquote", "section", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head", "title"):
            self.skip += 1
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n\n" + "#" * min(int(tag[1]) + 1, 6) + " ")
        elif tag in self.BLOCK:
            self.out.append("\n\n" + ("- " if tag == "li" else ""))
        elif tag in ("b", "strong"):
            self.out.append("**")
        elif tag in ("i", "em"):
            self.out.append("*")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "title"):
            self.skip = max(0, self.skip - 1)
        elif re.fullmatch(r"h[1-6]", tag) or tag in self.BLOCK:
            self.out.append("\n\n")
        elif tag in ("b", "strong"):
            self.out.append("**")
        elif tag in ("i", "em"):
            self.out.append("*")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(re.sub(r"\s+", " ", data))

    def text(self):
        t = "".join(self.out)
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"\n[ \t]+", "\n", t)
        t = re.sub(r"\*\*\s*\*\*|(?<!\*)\*\s*\*(?!\*)", "", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()


def html_to_md(src: str) -> str:
    p = HTML2MD()
    p.feed(src)
    return p.text()


def dehyphenate(text: str) -> str:
    """Une palabras cortadas al final de línea y las líneas de un mismo párrafo."""
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    paras = re.split(r"\n\s*\n", text)
    return "\n\n".join(re.sub(r"\s*\n\s*", " ", p).strip() for p in paras if p.strip())


def write_parts(out: Path, parts):
    out.mkdir(parents=True, exist_ok=True)
    for i, (heading, body) in enumerate(parts, 1):
        (out / f"parte_{i:03d}.md").write_text(f"# Parte {i}\n\n{heading}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"{len(parts)} partes escritas en {out}")


# ---------------------------------------------------------------- formatos
def from_pdf(path, out, first_page):
    import pymupdf
    doc = pymupdf.open(path)
    chars = [len(p.get_text().strip()) for p in doc]
    if sum(chars) < 50 * len(doc) * 0.2:   # casi sin texto: es un escaneo
        sys.exit("El PDF no tiene texto seleccionable (es un escaneo). Usa ocr_pdf.py y luego "
                 "revisa cada hoja contra su imagen (ver SKILL.md, paso 2).")
    sin_texto = [i + 1 for i, c in enumerate(chars) if c == 0]
    parts = []
    for i, page in enumerate(doc):
        num = (first_page + i) if first_page else (page.get_label() or i + 1)
        raw = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
        mid = page.rect.width / 2
        left = [b for b in raw if b[2] <= mid + 5]
        right = [b for b in raw if b[0] >= mid - 5]
        if len(left) >= 3 and len(right) >= 3 and len(left) + len(right) >= len(raw) * 0.9:
            # dos columnas (o dos páginas por hoja): primero toda la izquierda, luego la derecha
            raw.sort(key=lambda b: (0 if b[0] < mid - 5 else 1, b[1], b[0]))
        else:
            raw.sort(key=lambda b: (b[1], b[0]))
        paras = [dehyphenate(b[4]) for b in raw]          # cada bloque del PDF ≈ un párrafo
        parts.append((f"## Página {num}", "\n\n".join(paras) or "*(sin texto)*"))
    write_parts(out, parts)
    if sin_texto:
        print(f"Aviso: páginas del PDF sin texto (posibles imágenes/ilustraciones): {sin_texto[:20]}"
              f"{' …' if len(sin_texto) > 20 else ''}. Revísalas en imagen; si traen texto, usa OCR solo en ellas.")
    print("Revisa encabezados/pies repetidos y números de página dentro del texto, y elimínalos.")


def from_epub(path, out, _):
    z = zipfile.ZipFile(path)
    cont = ET.fromstring(z.read("META-INF/container.xml"))
    opf_path = cont.find(".//{*}rootfile").get("full-path")
    opf = ET.fromstring(z.read(opf_path))
    base = str(Path(opf_path).parent).replace("\\", "/")
    base = "" if base == "." else base + "/"
    manifest = {i.get("id"): i.get("href") for i in opf.find("{*}manifest")}
    parts, n = [], 0
    for ref in opf.find("{*}spine"):
        href = manifest.get(ref.get("idref"))
        if not href:
            continue
        md = html_to_md(z.read(base + href).decode("utf-8", errors="replace"))
        if len(md) < 40:      # portadillas vacías
            continue
        n += 1
        title = next((l.lstrip("# ").strip() for l in md.splitlines() if l.startswith("#")), "")
        parts.append((f"## Capítulo {n}" + (f": {title}" if title else ""), md))
    write_parts(out, parts)


def from_docx(path, out, _):
    z = zipfile.ZipFile(path)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(z.read("word/document.xml"))
    parts, cur_title, cur, n = [], None, [], 0
    for p in root.iter(f"{{{ns['w']}}}p"):
        style = p.find("w:pPr/w:pStyle", ns)
        style = style.get(f"{{{ns['w']}}}val", "") if style is not None else ""
        runs = []
        for r in p.findall("w:r", ns):
            t = "".join(x.text or "" for x in r.findall("w:t", ns))
            if not t:
                continue
            b = r.find("w:rPr/w:b", ns) is not None
            i = r.find("w:rPr/w:i", ns) is not None
            runs.append(f"**{t}**" if b and t.strip() else f"*{t}*" if i and t.strip() else t)
        text = "".join(runs).strip()
        if not text:
            continue
        level = re.search(r"(?:Heading|Ttulo|Título|Titulo)\s*(\d)", style, flags=re.I)
        if level and level.group(1) == "1":
            if cur or cur_title:
                parts.append((cur_title or "## Inicio", "\n\n".join(cur)))
            n += 1
            cur_title, cur = f"## Capítulo {n}: {text}", []
        elif level:
            cur.append("#" * (int(level.group(1)) + 1) + " " + text)
        else:
            cur.append(text)
    if cur or cur_title:
        parts.append((cur_title or "## Texto", "\n\n".join(cur)))
    write_parts(out, parts)


def from_text(path, out, _):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if Path(path).suffix.lower() in (".html", ".htm", ".xhtml"):
        text = html_to_md(text)
    elif Path(path).suffix.lower() == ".txt":
        text = dehyphenate(text)
    write_parts(out, [("## Texto completo", text)])
    print("Divide luego el texto en capítulos (## Capítulo N: título) si el libro los tiene.")


def from_other(path, out, first_page):
    if shutil.which("pandoc"):
        r = subprocess.run(["pandoc", str(path), "-t", "gfm", "--wrap=none"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0 and r.stdout.strip():
            write_parts(out, [("## Texto completo", r.stdout)])
            return
    try:
        import pymupdf
        doc = pymupdf.open(path)     # MOBI, FB2, XPS, CBZ…
        write_parts(out, [("## Texto completo", dehyphenate("\n\n".join(p.get_text() for p in doc)))])
        return
    except Exception as e:
        sys.exit(f"No pude abrir {path}: instala pandoc o conviértelo a PDF/EPUB/DOCX/TXT. ({e})")


HANDLERS = {".pdf": from_pdf, ".epub": from_epub, ".docx": from_docx,
            ".txt": from_text, ".md": from_text, ".html": from_text, ".htm": from_text, ".xhtml": from_text}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola Windows: python -I ignora PYTHONIOENCODING
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("libro"); ap.add_argument("salida")
    ap.add_argument("--primera-pagina", type=int, default=None,
                    help="PDF con texto: número impreso de la página 1 del PDF")
    a = ap.parse_args()
    path = Path(a.libro)
    if not path.exists():
        sys.exit(f"No existe {path}")
    HANDLERS.get(path.suffix.lower(), from_other)(path, Path(a.salida), a.primera_pagina)


if __name__ == "__main__":
    main()
