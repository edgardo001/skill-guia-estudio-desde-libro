"""Banco de pruebas de la skill. Se ejecuta con `python -I tests/run_tests.py`.

No necesita ningún libro real: usa `examples/libro_ejemplo.md`, que es inventado.

Qué comprueba:
  1. La plantilla genera una guía y verifica sus citas.
  2. Esa guía pasa `verificar_clave.py` y `verificar_citas.py`.
  3. Los verificadores SÍ fallan cuando hay un error puesto a propósito
     (una clave cambiada y una cita inventada). Un verificador que nunca falla
     no verifica nada.
  4. La plantilla de ampliación agrega preguntas, mantiene la coherencia y
     equilibra las letras.
  5. La plantilla se niega a escribir si una cita no está en el libro.

Si algo de esto falla, no publiques: la skill está rota para todos los libros.
"""
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "scripts"
EJEMPLOS = RAIZ / "examples"
LIBRO = EJEMPLOS / "libro_ejemplo.md"
DATOS = EJEMPLOS / "ejemplo_datos.json"
AMPLIACION = EJEMPLOS / "ejemplo_ampliacion.json"

resultados = []


def correr(*args, cwd=None):
    """Ejecuta un script de la skill y devuelve (código, salida)."""
    r = subprocess.run(
        [sys.executable, "-I", *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def comprobar(nombre, condicion, detalle=""):
    resultados.append((nombre, bool(condicion), detalle))
    print(("  OK   " if condicion else "  FALLA") + f"  {nombre}" + (f" — {detalle}" if not condicion and detalle else ""))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        quiz = tmp / "cuestionario.md"

        print("1. La plantilla genera la guía y verifica las citas")
        codigo, salida = correr(EJEMPLOS / "plantilla_guia.py", DATOS, LIBRO, quiz)
        comprobar("plantilla_guia.py termina sin error", codigo == 0, salida)
        comprobar("el cuestionario existe", quiz.exists())

        print("2. La guía generada pasa los dos verificadores")
        codigo, salida = correr(SCRIPTS / "verificar_clave.py", quiz)
        comprobar("verificar_clave.py: 0 errores", codigo == 0 and "Errores: 0" in salida, salida)
        codigo, salida = correr(SCRIPTS / "verificar_citas.py", quiz, LIBRO)
        comprobar("verificar_citas.py: 0 no encontradas", codigo == 0 and "no encontradas: 0" in salida, salida)

        print("3. Los verificadores detectan errores puestos a propósito")
        roto = tmp / "roto.md"
        texto = quiz.read_text(encoding="utf-8")
        # cambia la letra de la primera respuesta por otra que existe
        primera = re.search(r"^1\. \*\*([a-d])\) ", texto, flags=re.M)
        otra = "b" if primera.group(1) != "b" else "c"
        roto.write_text(texto[:primera.start(1)] + otra + texto[primera.end(1):], encoding="utf-8")
        codigo, salida = correr(SCRIPTS / "verificar_clave.py", roto)
        comprobar("verificar_clave.py falla con una clave cambiada", codigo == 1, salida)

        inventada = tmp / "inventada.md"
        inventada.write_text(texto + "\n1. **a) x** — *«una frase que el libro no dice»* (cap. 9)\n", encoding="utf-8")
        codigo, salida = correr(SCRIPTS / "verificar_citas.py", inventada, LIBRO)
        comprobar("verificar_citas.py falla con una cita inventada", codigo == 1, salida)

        print("4. La plantilla de ampliación agrega sin romper nada")
        codigo, salida = correr(EJEMPLOS / "ampliar_alternativas.py", AMPLIACION, quiz, LIBRO)
        comprobar("ampliar_alternativas.py termina sin error", codigo == 0, salida)
        codigo, salida = correr(SCRIPTS / "verificar_clave.py", quiz)
        comprobar("la guía ampliada sigue con 0 errores", codigo == 0 and "Errores: 0" in salida, salida)
        codigo, salida = correr(SCRIPTS / "verificar_citas.py", quiz, LIBRO)
        comprobar("la guía ampliada sigue con 0 citas faltantes",
                  codigo == 0 and "no encontradas: 0" in salida, salida)
        letras = Counter(re.findall(r"^\d+\. \*\*([a-d])\) ", quiz.read_text(encoding="utf-8"), flags=re.M))
        diferencia = max(letras.values()) - min(letras[l] for l in "abcd")
        comprobar("las letras quedan equilibradas (diferencia <= 3)", diferencia <= 3,
                  f"diferencia {diferencia}: {dict(sorted(letras.items()))}")

        print("5. La plantilla se niega a escribir con una cita falsa")
        datos = DATOS.read_text(encoding="utf-8").replace(
            "un faro blanco y solitario", "un faro rojo y luminoso", 1)
        falso = tmp / "datos_falsos.json"
        falso.write_text(datos, encoding="utf-8")
        salida_quiz = tmp / "no_debe_existir.md"
        codigo, salida = correr(EJEMPLOS / "plantilla_guia.py", falso, LIBRO, salida_quiz)
        comprobar("plantilla_guia.py falla con cita falsa", codigo == 1, salida)
        comprobar("y no escribe el archivo", not salida_quiz.exists())

        print("6. El OCR busca el modelo de español en el PROYECTO, no en la skill")
        proyecto = tmp / "proyecto_libro"
        (proyecto / "tessdata").mkdir(parents=True)
        (proyecto / "tessdata" / "spa.traineddata").write_bytes(b"modelo de prueba")
        codigo, salida = correr(SCRIPTS / "ocr_pdf.py", "no_existe.pdf", proyecto / "md", cwd=proyecto)
        comprobar("usa ./tessdata del proyecto y sigue hasta leer el PDF",
                  "No encontré spa.traineddata" not in salida and codigo == 1, salida)

    fallas = [n for n, ok, _ in resultados if not ok]
    print(f"\n{len(resultados) - len(fallas)}/{len(resultados)} pruebas OK")
    if fallas:
        print("FALLARON:")
        for n in fallas:
            print("  ✗", n)
        sys.exit(1)


if __name__ == "__main__":
    main()
