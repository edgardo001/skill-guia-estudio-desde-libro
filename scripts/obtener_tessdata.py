"""Descarga el modelo de español de Tesseract (spa.traineddata) para el OCR.

Uso:
    python -I scripts/obtener_tessdata.py [--destino CARPETA] [--rapido]

Se guarda en `tessdata/` de la **carpeta del proyecto** (donde está el libro), no en la skill:
así cada proyecto lleva lo suyo y la skill se mantiene sin binarios.

Sin --rapido usa tessdata_best (13 MB, la mejor calidad: la que conviene para libros
escaneados antiguos). Con --rapido usa tessdata_fast (2 MB, más rápido y menos exacto).

Si Tesseract ya tiene español en su propia carpeta tessdata, no hace falta descargar nada.
"""
import argparse
import sys
import urllib.request
from pathlib import Path

URLS = {
    "best": "https://github.com/tesseract-ocr/tessdata_best/raw/main/spa.traineddata",
    "fast": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata",
}
MINIMO = {"best": 8_000_000, "fast": 500_000}  # para detectar descargas truncadas o páginas de error


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", default=str(Path.cwd() / "tessdata"),
                    help="carpeta de destino (por defecto, ./tessdata del proyecto actual)")
    ap.add_argument("--rapido", action="store_true", help="usar tessdata_fast (2 MB)")
    a = ap.parse_args()

    variante = "fast" if a.rapido else "best"
    destino = Path(a.destino)
    archivo = destino / "spa.traineddata"
    destino.mkdir(parents=True, exist_ok=True)

    if archivo.exists() and archivo.stat().st_size >= MINIMO[variante]:
        print(f"Ya está: {archivo} ({archivo.stat().st_size / 1e6:.1f} MB)")
        return

    print(f"Descargando {variante}: {URLS[variante]}")
    try:
        with urllib.request.urlopen(URLS[variante], timeout=60) as r:
            datos = r.read()
    except Exception as e:
        sys.exit(f"No se pudo descargar: {e}\n"
                 f"Descárgalo a mano y guárdalo como {archivo}")

    if len(datos) < MINIMO[variante]:
        sys.exit(f"La descarga parece incompleta ({len(datos)} bytes). No se guardó nada.")

    archivo.write_bytes(datos)
    print(f"OK: {archivo} ({len(datos) / 1e6:.1f} MB)")
    print("Sugerencia: agrega 'tessdata/' al .gitignore del proyecto.")


if __name__ == "__main__":
    main()
