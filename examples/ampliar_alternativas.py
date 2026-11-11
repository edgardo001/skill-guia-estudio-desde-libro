"""PLANTILLA: agrega preguntas de alternativas al final de la actividad A de cada parte.

No contiene datos de ningún libro. Los del ejemplo (`ejemplo_ampliacion.json`) son
inventados. Sirve para ampliar una guía ya verificada sin renumerar lo que existe.

Uso:
    python -I ampliar_alternativas.py [nuevas.json] [cuestionario.md] [libro.md]

    nuevas.json     por defecto `ejemplo_ampliacion.json`, junto a este script
    cuestionario.md por defecto `cuestionario.md` en la carpeta actual (se modifica)
    libro.md        opcional; si se indica, se verifica cada cita nueva y el
                    resultado final antes de escribir

Qué hace:
  - Agrega cada pregunta al final de la actividad A de su sección, sin tocar la
    numeración anterior.
  - Agrega su respuesta al final del bloque "A. Alternativas" de esa sección.
  - Elige la letra correcta de cada pregunta nueva para que el total de a, b, c
    y d quede equilibrado (nunca cambia las letras de las preguntas ya hechas).
  - Se niega a escribir si una cita no está en el libro o si una pregunta nueva
    repite el enunciado de una que ya existe.

Formato del JSON: { "Parte I": [ {pregunta, correcta, distractores[3], cita|nota,
ubicacion}, … ], "Parte II": [ … ] }
La clave es el título exacto de la sección, tal como aparece en "## Parte …".
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

LETRAS = "abcd"
SEED = 20260101


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def seccion_cuerpo(texto, titulo, nivel):
    """Devuelve (inicio, fin) del cuerpo de la sección `## titulo` o `### titulo`."""
    m = re.search(rf"\n{nivel} {re.escape(titulo)}\n", texto)
    if not m:
        return None
    ini = m.end()
    sig = re.search(rf"\n{nivel} |\n## ", texto[ini:])
    fin = ini + sig.start() + 1 if sig else len(texto)
    return ini, fin


def ultimo_numero(cuerpo):
    nums = re.findall(r"^\*\*(\d+)\. ", cuerpo, flags=re.M)
    return max((int(n) for n in nums), default=0)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    aqui = Path(__file__).resolve().parent
    args = sys.argv[1:]
    nuevas_path = Path(args[0]) if len(args) > 0 else aqui / "ejemplo_ampliacion.json"
    quiz_path = Path(args[1]) if len(args) > 1 else Path.cwd() / "cuestionario.md"
    libro = Path(args[2]).read_text(encoding="utf-8") if len(args) > 2 else None

    nuevas = json.loads(nuevas_path.read_text(encoding="utf-8"))
    texto = quiz_path.read_text(encoding="utf-8")
    if "\n## Respuestas" not in texto:
        sys.exit("No encontré '## Respuestas' en el cuestionario.")
    preguntas, respuestas = texto.split("\n## Respuestas", 1)
    respuestas = "\n## Respuestas" + respuestas

    # ---- verificación previa ----
    if libro is not None:
        book = norm(libro.replace("\\*", "*"))
        faltan = [it["cita"] for items in nuevas.values() for it in items
                  if it.get("cita") and norm(it["cita"]) not in book]
        if faltan:
            print(f"CITAS NO ENCONTRADAS ({len(faltan)}); no se escribió nada:")
            for q in faltan:
                print("  ✗", q)
            sys.exit(1)
    ya_preguntadas = set(re.findall(r"^\*\*\d+\. (.+?)\*\*$", preguntas, flags=re.M))
    repetidas = [it["pregunta"] for items in nuevas.values() for it in items
                 if norm(it["pregunta"]) in {norm(x) for x in ya_preguntadas}]
    if repetidas:
        print("PREGUNTAS REPETIDAS; no se escribió nada:")
        for q in repetidas:
            print("  ✗", q)
        sys.exit(1)

    # ---- letras: equilibrar el total sin tocar lo ya hecho ----
    rng = random.Random(SEED)
    conteo = Counter(re.findall(r"^\d+\. \*\*([a-d])\) ", respuestas, flags=re.M))
    total_nuevas = sum(len(v) for v in nuevas.values())

    def siguiente_letra():
        return min(LETRAS, key=lambda l: (conteo[l], rng.random()))

    agregadas = 0
    for titulo, items in nuevas.items():
        pos = seccion_cuerpo(preguntas, titulo, "##")
        if pos is None:
            sys.exit(f"No encontré la sección '## {titulo}' en el cuestionario.")
        ini, fin = pos
        cuerpo = preguntas[ini:fin]
        n0 = ultimo_numero(cuerpo)

        bloque_q, bloque_k = "", ""
        for i, it in enumerate(items, n0 + 1):
            l = siguiente_letra()
            conteo[l] += 1
            opts = list(it["distractores"])
            rng.shuffle(opts)
            opts.insert(LETRAS.index(l), it["correcta"])
            bloque_q += (f"**{i}. {it['pregunta']}**\n\n"
                         + "".join(f"- {x}) {o}\n" for x, o in zip(LETRAS, opts)) + "\n")
            ev = f" — *«{it['cita']}»*" if it.get("cita") else f" — {it.get('nota', '')}"
            ub = f" ({it['ubicacion']})" if it.get("ubicacion") else ""
            bloque_k += f"{i}. **{l}) {it['correcta']}**{ev}{ub}\n"
            agregadas += 1

        # preguntas: antes de "### B." o al final de la sección
        corte = cuerpo.find("### B.")
        if corte >= 0:
            nuevo = cuerpo[:corte].rstrip("\n") + "\n\n" + bloque_q.rstrip("\n") + "\n\n" + cuerpo[corte:]
        else:
            nuevo = cuerpo.rstrip("\n") + "\n\n" + bloque_q.rstrip("\n") + "\n"
        preguntas = preguntas[:ini] + nuevo + preguntas[fin:]

        # respuestas: antes de "**B." o al final de la sección
        pos = seccion_cuerpo(respuestas, titulo, "###")
        if pos is None:
            sys.exit(f"No encontré el bloque de respuestas '### {titulo}'.")
        ini, fin = pos
        cuerpo = respuestas[ini:fin]
        corte = cuerpo.find("**B.")
        if corte >= 0:
            nuevo = cuerpo[:corte].rstrip("\n") + "\n" + bloque_k.rstrip("\n") + "\n\n" + cuerpo[corte:]
        else:
            nuevo = cuerpo.rstrip("\n") + "\n" + bloque_k
        respuestas = respuestas[:ini] + nuevo + respuestas[fin:]

    final = preguntas + respuestas

    if libro is not None:
        book = norm(libro.replace("\\*", "*"))
        citas = [norm(q).rstrip("…").strip() for q in re.findall(r"«([^»]+)»", final)]
        faltan = sorted({q for q in citas if q and q not in book})
        if faltan:
            print("CITAS NO ENCONTRADAS EN EL RESULTADO; no se escribió nada:")
            for q in faltan:
                print("  ✗", q)
            sys.exit(1)

    quiz_path.write_text(final, encoding="utf-8")
    print(f"OK: {agregadas} preguntas agregadas · letras ahora: {dict(sorted(conteo.items()))}")
    print("Vuelve a ejecutar verificar_clave.py y verificar_citas.py.")


if __name__ == "__main__":
    main()
