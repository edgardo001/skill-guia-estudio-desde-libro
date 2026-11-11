"""PLANTILLA: arma `cuestionario.md` a partir de un archivo de datos JSON.

No contiene datos de ningún libro. Los del ejemplo (`ejemplo_datos.json`) son
inventados; para tu libro, copia el JSON, reemplaza el contenido y ejecuta.

Uso:
    python -I plantilla_guia.py [datos.json] [libro.md] [salida.md]

    datos.json  por defecto `ejemplo_datos.json`, junto a este script
    libro.md    texto completo del libro (`md/libro_completo.md`). Si se indica,
                TODA cita «…» se verifica contra él antes de escribir nada.
    salida.md   por defecto `cuestionario.md` en la carpeta actual

Qué hace:
  - Reparte las letras correctas de las actividades A y E de forma equilibrada
    (a, b, c, d) con una semilla fija, en lugar de dejarlas todas en "a".
  - Desordena las alternativas y los hechos de la actividad C (el orden de
    presentación no puede ser el de la respuesta).
  - Genera exactamente el formato que esperan `verificar_clave.py` y
    `generar_pdf.py`. Si `verificar_clave.py` falla con esta plantilla, es un
    error de la plantilla: avísalo.
  - No escribe el archivo si alguna cita no está literalmente en el libro.

Formato del JSON (ver `ejemplo_datos.json`):
  titulo, autor, importante, como_usar[]
  secciones[]: titulo
               a[]: pregunta, correcta, distractores[3], cita | nota, ubicacion
               personajes[3-6]  (para la actividad B)
               b[]: cita, quien, ubicacion
               c:   hechos[]: texto, orden  ·  ubicacion
               d[]: afirmacion, vof ("V"/"F"), cita, ubicacion
               e[]: contexto, palabra, correcta, distractores[3], ubicacion
               f[]: pregunta, idea, cita, ubicacion  |  pregunta, personal, pista
  cierre: titulo, preguntas[] (mismo formato que f)

`ubicacion` se escribe tal cual aparece en la respuesta: "cap. 3", "pág. 12",
"págs. 12–13" o "Portada". Un libro con páginas impresas usa "pág. X" (el número
impreso, no el del PDF); un libro sin páginas usa "cap. N".
"""
import json
import random
import re
import sys
from pathlib import Path

LETRAS = "abcd"
SEED = 20260101


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def repartir_letras(n, rng):
    """Reparte n letras entre a, b, c y d con la menor diferencia posible."""
    base, extra = divmod(n, len(LETRAS))
    pool = [l for i, l in enumerate(LETRAS) for _ in range(base + (1 if i < extra else 0))]
    rng.shuffle(pool)
    return pool


def alternativas(item, letra, rng):
    opts = list(item["distractores"])
    rng.shuffle(opts)
    opts.insert(LETRAS.index(letra), item["correcta"])
    return opts


def linea_ubicacion(item):
    return f" ({item['ubicacion']})" if item.get("ubicacion") else ""


def evidencia(item):
    """Devuelve ' — *«cita»* (ubicación)' o ' — nota'."""
    if item.get("cita"):
        return f" — *«{item['cita']}»*{linea_ubicacion(item)}"
    if item.get("nota"):
        return f" — {item['nota']}"
    return ""


def respuesta_f(item):
    if item.get("personal"):
        return f"Respuesta personal. Pista: {item['pista']}"
    return f"{item['idea']}{evidencia(item)}"


def render(datos, seed=SEED):
    L = []
    w = L.append
    rng = random.Random(seed)

    w("# Guía de estudio")
    w("")
    w(f"## *{datos['titulo']}* — {datos['autor']}")
    w("")
    w("**Nombre:** ______________________________")
    w("")
    w("### ¿Cómo usar esta guía?")
    w("")
    for i, paso in enumerate(datos.get("como_usar", []), 1):
        w(f"{i}. {paso}")
    w("")
    if datos.get("importante"):
        w(f"**Importante:** {datos['importante']}")
        w("")
    w("---")
    w("")

    secciones = datos["secciones"]
    letras_a = repartir_letras(sum(len(s.get("a", [])) for s in secciones), random.Random(seed))
    letras_e = repartir_letras(sum(len(s.get("e", [])) for s in secciones), random.Random(seed + 1))
    ia = ie = 0

    # ---------- preguntas ----------
    for i, sec in enumerate(secciones):
        inicial = sec["titulo"].lower().startswith("sección inicial")
        w(f"## {sec['titulo']}")
        w("")
        w("### Elige la alternativa correcta" if inicial else "### A. Elige la alternativa correcta")
        w("")
        for n, item in enumerate(sec.get("a", []), 1):
            opts = alternativas(item, letras_a[ia], rng)
            ia += 1
            w(f"**{n}. {item['pregunta']}**")
            w("")
            for l, o in zip(LETRAS, opts):
                w(f"- {l}) {o}")
            w("")
        if inicial:
            w("---")
            w("")
            continue

        w("### B. ¿Quién lo dijo?")
        w("")
        w("Escribe quién dijo cada frase. Elige entre: "
          + ", ".join(f"*{x}*" for x in sec.get("personajes", [])) + ".")
        w("")
        for n, item in enumerate(sec.get("b", []), 1):
            w(f"{n}. «{item['cita']}» Lo dijo: ____________________")
            w("")

        w("### C. Ordena los hechos")
        w("")
        hechos = list(sec["c"]["hechos"])
        presentados = hechos[:]
        rng.shuffle(presentados)
        w(f"Escribe del 1 al {len(hechos)} en qué orden ocurrieron.")
        w("")
        for h in presentados:
            w(f"- ( ) {h['texto']}")
        w("")

        w("### D. ¿Verdadero o falso?")
        w("")
        w("Escribe **V** si es verdadero o **F** si es falso.")
        w("")
        for n, item in enumerate(sec.get("d", []), 1):
            w(f"{n}. ( ) {item['afirmacion']}")
            w("")

        w("### E. Aprende palabras nuevas")
        w("")
        for n, item in enumerate(sec.get("e", []), 1):
            opts = alternativas(item, letras_e[ie], rng)
            ie += 1
            w(f"**{n}. En la frase «{item['contexto']}…»{linea_ubicacion(item)}, "
              f"¿qué significa *{item['palabra']}*?**")
            w("")
            for l, o in zip(LETRAS, opts):
                w(f"- {l}) {o}")
            w("")

        w("### F. Piensa y responde")
        w("")
        for n, item in enumerate(sec.get("f", []), 1):
            w(f"**{n}. {item['pregunta']}**")
            w("")
            w("_______________________________________________")
            w("")
            w("_______________________________________________")
            w("")
        w("---")
        w("")

    cierre = datos.get("cierre")
    if cierre:
        w(f"## {cierre['titulo']}")
        w("")
        for n, item in enumerate(cierre["preguntas"], 1):
            w(f"**{n}. {item['pregunta']}**")
            w("")
            w("_______________________________________________")
            w("")
            w("_______________________________________________")
            w("")
        w("---")
        w("")

    # ---------- respuestas ----------
    w("## Respuestas")
    w("")
    w("Revisa aquí tus respuestas **después** de contestar. Cada respuesta trae la "
      "frase del libro que la explica y dónde encontrarla.")
    w("")
    ia = ie = 0

    for sec in secciones:
        inicial = sec["titulo"].lower().startswith("sección inicial")
        w(f"### {sec['titulo']}")
        w("")
        if not inicial:
            w("**A. Alternativas**")
            w("")
        for n, item in enumerate(sec.get("a", []), 1):
            l = letras_a[ia]
            ia += 1
            w(f"{n}. **{l}) {item['correcta']}**{evidencia(item)}")
        w("")
        if inicial:
            continue

        w("**B. ¿Quién lo dijo?**")
        w("")
        for n, item in enumerate(sec.get("b", []), 1):
            quien = item["quien"]
            w(f"{n}. {quien[0].upper() + quien[1:]}{linea_ubicacion(item)}")
        w("")

        w("**C. Orden de los hechos**")
        w("")
        for h in sorted(sec["c"]["hechos"], key=lambda x: x["orden"]):
            w(f"{h['orden']}. {h['texto']}")
        if sec["c"].get("ubicacion"):
            w("")
            w(f"*({sec['c']['ubicacion']})*")
        w("")

        w("**D. Verdadero o falso**")
        w("")
        for n, item in enumerate(sec.get("d", []), 1):
            w(f"{n}. **{item['vof']}**{evidencia(item)}")
        w("")

        w("**E. Palabras nuevas**")
        w("")
        for n, item in enumerate(sec.get("e", []), 1):
            l = letras_e[ie]
            ie += 1
            w(f"{n}. **{l}) {item['correcta']}**")
        w("")

        w("**F. Piensa y responde** *(son ideas de respuesta; lo importante es que "
          "lo expliques con tus palabras)*")
        w("")
        for n, item in enumerate(sec.get("f", []), 1):
            w(f"{n}. {respuesta_f(item)}")
        w("")

    if cierre:
        w(f"### {cierre['titulo']}")
        w("")
        for n, item in enumerate(cierre["preguntas"], 1):
            w(f"{n}. {respuesta_f(item)}")
        w("")

    return "\n".join(L).rstrip() + "\n"


def citas_faltantes(md, libro):
    """Misma regla que verificar_citas.py: cada «…» debe estar en el libro."""
    book = norm(libro.replace("\\*", "*"))
    quotes = [norm(q).rstrip("…").strip() for q in re.findall(r"«([^»]+)»", md)]
    return sorted({q for q in quotes if q and q not in book})


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    aqui = Path(__file__).resolve().parent
    args = sys.argv[1:]
    datos_path = Path(args[0]) if len(args) > 0 else aqui / "ejemplo_datos.json"
    libro_path = Path(args[1]) if len(args) > 1 else None
    salida = Path(args[2]) if len(args) > 2 else Path.cwd() / "cuestionario.md"

    datos = json.loads(datos_path.read_text(encoding="utf-8"))
    md = render(datos)

    if libro_path:
        faltan = citas_faltantes(md, libro_path.read_text(encoding="utf-8"))
        if faltan:
            print(f"CITAS NO ENCONTRADAS ({len(faltan)}); no se escribió nada:")
            for q in faltan:
                print("  ✗", q)
            sys.exit(1)
        print(f"Citas verificadas contra {libro_path.name}: todas presentes.")

    salida.write_text(md, encoding="utf-8")
    n_a = sum(len(s.get("a", [])) for s in datos["secciones"])
    print(f"OK: {salida} · {n_a} preguntas de alternativas · "
          f"{len(datos['secciones'])} secciones")


if __name__ == "__main__":
    main()
