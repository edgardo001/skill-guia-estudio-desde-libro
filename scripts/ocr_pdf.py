"""Borrador OCR de un libro escaneado en PDF -> un .md por hoja.

Uso:
    python -I scripts/ocr_pdf.py LIBRO.pdf CARPETA_SALIDA [--tessdata DIR] [--paginas-por-hoja 2] [--primera-pagina N]

- Si el PDF ya tiene texto seleccionable, NO uses este script: extrae con PyMuPDF (page.get_text()).
- Renderiza cada hoja a 300 dpi, blanquea los colores saturados (ilustraciones), separa en
  izquierda/derecha si cada hoja trae 2 páginas del libro, aplica Tesseract en español y
  reconstruye párrafos (une guiones de corte de palabra).
- El resultado es un BORRADOR: hay que revisarlo hoja por hoja contra la imagen (ver SKILL.md).

Requisitos: pip install pymupdf pillow numpy ; Tesseract instalado ; el modelo de español.
  Si falta spa.traineddata, ejecuta `python -I scripts/obtener_tessdata.py`: lo descarga en
  ./tessdata de ESTE proyecto (agrega tessdata/ a su .gitignore). También sirve el que ya
  tenga Tesseract instalado en su propia carpeta tessdata.
"""
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜáéíóúüÑñ]")


def find_tesseract():
    for c in (os.environ.get("TESSERACT", ""), shutil.which("tesseract") or "",
              r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        if c and Path(c).exists():
            return c
    sys.exit("No encontré Tesseract. Instálalo o define la variable TESSERACT.")


def resolver_tessdata(dado, tess):
    """Devuelve una carpeta que contenga spa.traineddata, o se detiene con instrucciones.

    Orden: --tessdata · tessdata/ del proyecto (carpeta actual) · TESSDATA_PREFIX ·
    la carpeta tessdata de la propia instalación de Tesseract.
    """
    candidatos = []
    if dado:
        candidatos.append(Path(dado))
    candidatos.append(Path.cwd() / "tessdata")
    for var in ("TESSDATA_PREFIX",):
        if os.environ.get(var):
            candidatos.append(Path(os.environ[var]))
    candidatos.append(Path(tess).resolve().parent / "tessdata")
    candidatos += [Path.home() / "AppData/Local/tesseract/tessdata",
                   Path("/usr/share/tesseract-ocr/5/tessdata"),
                   Path("/usr/share/tessdata"),
                   Path("/usr/local/share/tessdata"),
                   Path("/opt/homebrew/share/tessdata")]
    for c in candidatos:
        if (c / "spa.traineddata").exists():
            return c
    sys.exit(
        "No encontré spa.traineddata (el modelo de español de Tesseract).\n"
        f"Busqué en: {', '.join(str(c) for c in candidatos)}\n"
        "Descárgalo una sola vez en la carpeta de este proyecto con:\n"
        "    python -I scripts/obtener_tessdata.py\n"
        "(lo guarda en ./tessdata; agrega 'tessdata/' al .gitignore del proyecto)\n"
        "o indica otra carpeta con --tessdata DIR."
    )


def ocr_tsv(tess, tessdata, path):
    r = subprocess.run([tess, str(path), "stdout", "--tessdata-dir", str(tessdata), "-l", "spa", "--psm", "4",
                        "-c", "tessedit_create_tsv=1"], capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def clean_edges(ws):
    junk = lambda w: w["conf"] < 55 or (not WORD.search(w["text"]) and w["text"] not in ("—", "-"))
    while ws and junk(ws[0]) and not ws[0]["text"].startswith(("—", "¡", "¿")):
        ws = ws[1:]
    while ws and junk(ws[-1]):
        ws = ws[:-1]
    return ws


def lines_from_tsv(tsv):
    lines = {}
    for row in tsv.splitlines()[1:]:
        c = row.split("\t")
        if len(c) < 12 or c[0] != "5" or not c[11].strip():
            continue
        l, t, w, h = map(int, c[6:10])
        lines.setdefault((int(c[2]), int(c[3]), int(c[4])), []).append(
            dict(l=l, t=t, r=l + w, b=t + h, text=c[11].strip(), conf=float(c[10])))
    out = []
    for ws in lines.values():
        ws = clean_edges(sorted(ws, key=lambda w: w["l"]))
        if ws:
            out.append(dict(left=ws[0]["l"], right=ws[-1]["r"], top=min(w["t"] for w in ws),
                            bottom=max(w["b"] for w in ws), text=" ".join(w["text"] for w in ws),
                            conf=sum(w["conf"] for w in ws) / len(ws)))
    return sorted(out, key=lambda x: x["top"])


def join_lines(lines):
    s = ""
    for ln in lines:
        if s.endswith("-") and len(s) > 1 and s[-2].isalpha() and ln[:1].islower():
            s = s[:-1] + ln
        else:
            s = f"{s} {ln}" if s else ln
    return s.replace(" ,", ",")


def to_paragraphs(lines, height, top=0.165, bottom=0.86):
    """top/bottom: fracción de la altura que se descarta (encabezados, sellos, números de página)."""
    body = [l for l in lines if height * top < l["top"] and l["bottom"] < height * bottom
            and l["conf"] > 45 and len(WORD.findall(l["text"])) >= 2]
    if not body:
        return []
    max_right = sorted(l["right"] for l in body)[int(len(body) * 0.75)]
    margin = sorted(l["left"] for l in body)[len(body) // 4]
    lh = sorted(l["bottom"] - l["top"] for l in body)[len(body) // 2]
    paras, cur, prev = [], [], None
    for l in body:
        if prev and cur:
            ends = re.search(r"[.!?:»\"”]$", prev["text"])
            short = prev["right"] < max_right - lh * 1.5
            indent = abs(prev["left"] - margin) < lh and l["left"] - margin > lh * 0.8
            gap = l["top"] - prev["bottom"] > lh * 0.9
            if ends and (short or indent or gap or l["text"].startswith("—")):
                paras.append(cur); cur = []
        cur.append(l["text"]); prev = l
    if cur:
        paras.append(cur)
    return [join_lines(p) for p in paras]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola Windows: python -I ignora PYTHONIOENCODING
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("salida")
    ap.add_argument("--tessdata", default=None,
                    help="carpeta con spa.traineddata (por defecto, se busca sola)")
    ap.add_argument("--paginas-por-hoja", type=int, default=2, choices=(1, 2))
    ap.add_argument("--primera-pagina", type=int, default=None,
                    help="número impreso de la página izquierda de la hoja 1 (si se conoce)")
    ap.add_argument("--imagenes", default=None, help="carpeta donde guardar las imágenes de cada hoja")
    a = ap.parse_args()

    tess = find_tesseract()
    tessdata = resolver_tessdata(a.tessdata, tess)
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    img_dir = Path(a.imagenes or out / "_imagenes"); img_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    for i, page in enumerate(doc, 1):
        png = img_dir / f"p{i:03d}.png"
        page.get_pixmap(dpi=300).save(png)
        im = Image.open(png)
        hsv, g = np.array(im.convert("HSV")), np.array(im.convert("L"))
        im = Image.fromarray(np.where(hsv[..., 1] > 70, 255, g).astype("uint8"))  # quita ilustraciones a color
        W, H = im.size
        boxes = [(0, 0, W // 2, H), (W // 2, 0, W, H)] if a.paginas_por_hoja == 2 else [(0, 0, W, H)]
        md = [f"# Hoja {i} del PDF", ""]
        for k, box in enumerate(boxes):
            half = img_dir / f"p{i:03d}_{k}.png"
            im.crop(box).save(half)
            paras = to_paragraphs(lines_from_tsv(ocr_tsv(tess, a.tessdata, half)), H)
            num = (a.primera_pagina + (i - 1) * a.paginas_por_hoja + k) if a.primera_pagina else "?"
            md += [f"## Página {num}", ""] + [x for p in paras for x in (p, "")] + ([] if paras else ["*(sin texto)*", ""])
        (out / f"hoja_{i:03d}.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")
        print(f"hoja {i}/{doc.page_count}", flush=True)


if __name__ == "__main__":
    main()
