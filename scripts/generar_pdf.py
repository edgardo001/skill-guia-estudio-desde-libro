"""Genera un PDF imprimible (A4 horizontal, 2 columnas) a partir de un cuestionario en Markdown.

Uso:
    python generar_pdf.py [entrada.md] [salida.pdf]

Por defecto: ./cuestionario.md (carpeta actual) -> cuestionario_vAAAA.MM.DD.HHMM.pdf (junto a la entrada).
El PDF SIEMPRE se crea versionado con la fecha y hora de generación, por ejemplo
cuestionario_v2026.11.10.1628.pdf; nunca se sobrescribe una versión anterior. Si se indica
salida.pdf, se usa su carpeta y nombre base: salida_v2026.11.10.1628.pdf. Si ya existe un
archivo con ese nombre (dos generaciones en el mismo minuto), se agrega un sufijo: _2, _3…

Requiere:  pip install reportlab

Markdown soportado (el que usa la guía):
    # Título              ## Sección (franja de color)     ### Subsección
    **N. Pregunta**       seguida de "- a) ..." (se mantiene junta, sin partirse entre columnas)
    1. ítem numerado      - ítem con viñeta                 ---  (línea separadora)
    **negrita**, *cursiva*, \\* (asterisco literal)
La sección que empieza con "## Respuestas" se imprime desde una página nueva.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer)
from reportlab.platypus.flowables import HRFlowable

HERE = Path(__file__).resolve().parent
ACENTO = colors.HexColor("#1f5f8b")
SUAVE = colors.HexColor("#e8f1f7")
LINEA = colors.HexColor("#c9d6df")

# ---------------------------------------------------------------- fuentes
FONT_DIRS = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")]
FAMILIES = [  # (nombre, normal, negrita, cursiva, negrita-cursiva)
    ("Georgia", "georgia.ttf", "georgiab.ttf", "georgiai.ttf", "georgiaz.ttf"),
    ("Arial", "arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
    ("DejaVuSerif", "DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf", "DejaVuSerif-BoldItalic.ttf"),
]


def register_font():
    for name, *files in FAMILIES:
        for d in FONT_DIRS:
            paths = [d / f for f in files]
            if all(p.exists() for p in paths):
                for suffix, p in zip(("", "-Bold", "-Italic", "-BoldItalic"), paths):
                    pdfmetrics.registerFont(TTFont(name + suffix, str(p)))
                pdfmetrics.registerFontFamily(name, normal=name, bold=name + "-Bold",
                                              italic=name + "-Italic", boldItalic=name + "-BoldItalic")
                return name
    return "Helvetica"  # fuente base de PDF (soporta tildes y ñ)


FONT = register_font()


def st(name, **kw):
    base = dict(fontName=FONT, fontSize=10.5, leading=13.5, alignment=TA_LEFT, spaceAfter=2)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "h1": st("h1", fontSize=22, leading=26, textColor=ACENTO, spaceAfter=4),
    "h2": st("h2", fontSize=13, leading=17, textColor=colors.white, backColor=ACENTO, borderPadding=(4, 5, 4, 5),
             spaceBefore=10, spaceAfter=8, keepWithNext=1),
    "h2sub": st("h2sub", fontSize=13, leading=16, textColor=colors.HexColor("#333333"), spaceAfter=6),
    "h3": st("h3", fontSize=11.5, leading=14, textColor=ACENTO, spaceBefore=7, spaceAfter=4, keepWithNext=1),
    "p": st("p", spaceAfter=4),
    "q": st("q", spaceBefore=5, spaceAfter=2, keepWithNext=1),
    "opt": st("opt", leftIndent=4 * mm, spaceAfter=0.5),
    "li": st("li", leftIndent=6 * mm, firstLineIndent=-5 * mm, spaceAfter=2.5),
    "box": st("box", backColor=SUAVE, borderPadding=(3, 5, 3, 5), leftIndent=0, spaceBefore=2, spaceAfter=2),
}
SMALL = {k: ParagraphStyle(k + "_s", parent=v, fontSize=v.fontSize - 1, leading=v.leading - 1.5) for k, v in S.items()}


# ---------------------------------------------------------------- markdown -> flowables
def inline(text):
    text = text.replace("\\*", "\x00")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<![\w_])_(?!_)(.+?)(?<!_)_(?![\w_])", r"<i>\1</i>", text)
    return text.replace("\x00", "*")


def blocks(md):
    """Agrupa líneas en bloques: separados por líneas en blanco."""
    cur = []
    for line in md.splitlines():
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            yield cur
            cur = []
    if cur:
        yield cur


def build_story(md):
    story, styles = [], S
    pending_q = None          # pregunta en negrita esperando sus alternativas
    in_box = False            # bloque "¿Cómo usar esta guía?"
    last_hr = False

    def flush_q():
        nonlocal pending_q
        if pending_q is not None:
            story.append(pending_q)
            pending_q = None

    for blk in blocks(md):
        first = blk[0]
        if re.fullmatch(r"-{3,}", first.strip()):
            flush_q()
            if not last_hr:
                story.append(HRFlowable(width="100%", thickness=0.6, color=LINEA, dash=(2, 2),
                                        spaceBefore=4, spaceAfter=4))
            last_hr = True
            in_box = False
            continue
        last_hr = False

        if first.startswith("# "):
            flush_q(); story.append(Paragraph(inline(first[2:]), styles["h1"])); continue
        if first.startswith("## "):
            flush_q(); in_box = False
            title = first[3:]
            if title.startswith("Respuestas"):
                story.append(PageBreak())
                styles = SMALL
            if title.startswith("*"):   # subtítulo de portada
                story.append(Paragraph(inline(title), styles["h2sub"]))
            else:
                story.append(Paragraph(inline(title), styles["h2"]))
            continue
        if first.startswith("### "):
            flush_q()
            title = first[4:]
            in_box = title.startswith("¿Cómo usar")
            story.append(Paragraph(inline(title), styles["h3"]))
            continue

        # listas (alternativas "- a) ..." o numeradas "1. ...")
        if all(re.match(r"(- |\d+\. )", l) for l in blk):
            items = []
            for l in blk:
                if l.startswith("- "):
                    items.append(Paragraph(inline(l[2:]), styles["opt"]))
                else:
                    n, rest = l.split(". ", 1)
                    items.append(Paragraph(f"{n}.&nbsp;&nbsp;" + inline(rest), styles["box" if in_box else "li"]))
            if pending_q is not None and blk[0].startswith("- "):
                story.append(KeepTogether([pending_q] + items))
                pending_q = None
            else:
                flush_q()
                story.extend(items)
            continue

        # párrafo normal (puede ocupar varias líneas)
        flush_q()
        text = " ".join(l.strip() for l in blk)
        if re.match(r"\*\*\d+\. ", text):
            pending_q = Paragraph(inline(text), styles["q"])
        elif re.fullmatch(r"\*\*[^*]+\*\*.*", text) and len(text) < 120:
            # subtítulo en negrita (p. ej. "**A. Alternativas**"): no dejarlo solo al final de una columna
            story.append(Paragraph(inline(text), ParagraphStyle("sub", parent=styles["p"], keepWithNext=1, spaceBefore=4)))
        else:
            story.append(Paragraph(inline(text), styles["box" if in_box else "p"]))
    flush_q()
    return story


# ---------------------------------------------------------------- documento
def make_pdf(src: Path, out: Path):
    page_w, page_h = landscape(A4)
    margin, gap, bottom = 12 * mm, 10 * mm, 14 * mm
    col_w = (page_w - 2 * margin - gap) / 2
    col_h = page_h - margin - bottom
    frames = [Frame(margin, bottom, col_w, col_h, id="izq", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
              Frame(margin + col_w + gap, bottom, col_w, col_h, id="der",
                    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)]
    title = next((l[2:] for l in src.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), src.stem)

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINEA)
        x = margin + col_w + gap / 2
        canvas.line(x, bottom, x, bottom + col_h)  # línea divisoria entre columnas
        canvas.setFont(FONT, 8.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawCentredString(page_w / 2, 7 * mm, f"{title}  ·  página {doc.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(str(out), pagesize=(page_w, page_h), title=title, author="",
                          leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=bottom)
    doc.addPageTemplates([PageTemplate(id="dos_columnas", frames=frames, onPage=decorate)])
    doc.build(build_story(src.read_text(encoding="utf-8")))


def versioned(base: Path) -> Path:
    """nombre.pdf -> nombre_vAAAA.MM.DD.HHMM.pdf (con sufijo _2, _3… si ya existe)."""
    stem = re.sub(r"_v\d{4}\.\d{2}\.\d{2}\.\d{4}(_\d+)?$", "", base.stem)  # no duplicar versiones
    out = base.with_name(f"{stem}_v{datetime.now():%Y.%m.%d.%H%M}.pdf")
    n = 2
    while out.exists():
        out = base.with_name(f"{stem}_v{datetime.now():%Y.%m.%d.%H%M}_{n}.pdf")
        n += 1
    return out


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "cuestionario.md"
    out = versioned(Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf"))
    if not src.exists():
        sys.exit(f"No existe el archivo {src}")
    make_pdf(src.resolve(), out.resolve())
    print(f"PDF generado: {out.resolve()}  (fuente: {FONT})")


if __name__ == "__main__":
    main()
