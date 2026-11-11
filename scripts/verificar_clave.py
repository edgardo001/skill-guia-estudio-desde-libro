"""Comprueba la coherencia interna de la guía (complementa a verificar_citas.py).

Uso:
    python -I scripts/verificar_clave.py cuestionario.md

Revisa, sección por sección (## Sección inicial / ## Parte …):
  - Actividad A: numeración 1..N sin saltos, 4 alternativas distintas, y que cada respuesta
    "N. **x) texto**" coincida exactamente con la alternativa x) de la pregunta N.
  - Actividad B: misma cantidad de frases que respuestas, y cada personaje de la respuesta está en la lista "Elige entre".
  - Actividad C: los hechos de la respuesta son los mismos de la pregunta y van numerados 1..5.
  - Actividad D: misma cantidad de afirmaciones que respuestas V/F.
Informa el total de preguntas de alternativas y la distribución de letras correctas.
Sale con código 1 si encuentra errores.

Formato esperado (el que genera la guía; ver references/flujo-completo.md):
  preguntas:  **N. Pregunta**  + líneas "- a) …" … "- d) …"
  respuestas: "## Respuestas", luego "### <mismo título de sección>", y dentro
              "N. **x) texto** — *«cita»* (pág. X)" o "(cap. N)" si el libro no tiene páginas; las actividades B–F después de "**B." etc.
"""
import re
import sys
from collections import Counter


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola Windows: python -I ignora PYTHONIOENCODING
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    t = open(sys.argv[1], encoding="utf-8").read()
    if "\n## Respuestas" not in t:
        sys.exit("No encontré la sección '## Respuestas'.")
    q, k = t.split("\n## Respuestas", 1)
    qsecs = re.split(r"\n## (?=Sección inicial|Parte )", q)[1:]
    ksecs = {s.split("\n")[0].strip(): s for s in re.split(r"\n### ", k)[1:]}
    errors, letters, total = [], Counter(), 0

    for qs in qsecs:
        name = qs.split("\n")[0].strip()
        ks = ksecs.get(name)
        if ks is None:
            errors.append(f"[{name}] no tiene bloque de respuestas '### {name}'")
            continue
        A = qs.split("### B.")[0]
        items = re.findall(r"\*\*(\d+)\. (.+?)\*\*\n\n((?:- .+\n)+)", A)
        keys = re.findall(r"^(\d+)\. \*\*(\w)\) (.+?)\*\*", ks.split("**B.")[0], flags=re.M)
        nums = [int(n) for n, _, _ in items]
        if nums != list(range(1, len(nums) + 1)):
            errors.append(f"[{name}] numeración de preguntas no es 1..{len(nums)}: {nums}")
        if len(items) != len(keys):
            errors.append(f"[{name}] {len(items)} preguntas pero {len(keys)} respuestas")
        for (n, qt, opts), (kn, l, txt) in zip(items, keys):
            o = {x[2]: x[5:] for x in opts.strip().split("\n")}
            if sorted(o) != list("abcd") or len(set(o.values())) != 4:
                errors.append(f"[{name}] P{n}: no tiene 4 alternativas a–d distintas")
            if n != kn:
                errors.append(f"[{name}] P{n}: la respuesta está numerada {kn}")
            elif o.get(l) != txt:
                errors.append(f"[{name}] P{n}: clave '{l}) {txt}' ≠ alternativa '{l}) {o.get(l)}'")
            letters[l] += 1
        total += len(items)

        if "### B." in qs:
            B = qs.split("### B.")[1].split("### C.")[0]
            frases = re.findall(r"«(.+?)»", B)
            bank = re.search(r"Elige entre: (.+)\.\n", B)
            kb = re.findall(r"^\d+\. (.+?) \((?:pág|cap)", ks.split("**B.")[1].split("**C.")[0], flags=re.M)
            if len(frases) != len(kb):
                errors.append(f"[{name}] B: {len(frases)} frases y {len(kb)} respuestas")
            if bank:
                for x in kb:
                    if f"*{x.lower()}*" not in bank.group(1).lower():
                        errors.append(f"[{name}] B: '{x}' no está en la lista 'Elige entre'")
        if "### C." in qs:
            C = qs.split("### C.")[1].split("### D.")[0]
            ev = re.findall(r"- \( \) (.+)", C)
            kc = re.findall(r"^(\d)\. (.+)$", ks.split("**C.")[1].split("**D.")[0], flags=re.M)
            if sorted(ev) != sorted(s for _, s in kc):
                errors.append(f"[{name}] C: los hechos de la respuesta no son los mismos de la pregunta")
            if [int(n) for n, _ in kc] != list(range(1, len(kc) + 1)):
                errors.append(f"[{name}] C: la respuesta no está numerada 1..{len(kc)}")
        if "### D." in qs:
            D = re.findall(r"^\d+\. \( \) ", qs.split("### D.")[1].split("### E.")[0], flags=re.M)
            kd = re.findall(r"^\d+\. \*\*[VF]\*\*", ks.split("**D.")[1].split("**E.")[0], flags=re.M)
            if len(D) != len(kd):
                errors.append(f"[{name}] D: {len(D)} afirmaciones y {len(kd)} respuestas V/F")
        print(f"{name}: {len(items)} preguntas de alternativas")

    print(f"Total alternativas: {total} · letras correctas: {dict(sorted(letters.items()))}")
    if total:
        spread = max(letters.values()) - min(letters[l] for l in "abcd")
        if spread > max(3, total // 20):
            print(f"  ⚠ letras desequilibradas (diferencia {spread}); reordena alternativas")
    for e in errors:
        print("  ✗", e)
    print("Errores:", len(errors))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
