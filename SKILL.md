---
name: guia-estudio-desde-libro
license: MIT
description: Use when a folder contains a book or long text (scanned PDF, PDF with text, EPUB, DOCX, TXT, HTML, ODT, MOBI…) and the user wants its full text extracted to Markdown, a summary, or a study guide, quiz, questionnaire or reading-comprehension questions with answers verified against the source and no hallucinations — typically for children or students, with a printable PDF. Spanish triggers - libro, resumen, cuestionario, guía de estudio, preguntas de alternativas, comprensión lectora, prueba para un niño.
---

# De un libro a material de estudio verificado

## Cuándo se usa

El usuario deja un libro en una carpeta y dice algo como *"trabaja con este documento"*,
*"sácame el texto"*, *"hazme un resumen"* o *"hazme un cuestionario"*. Tú te encargas del
resto: no le pides comandos, rutas ni nombres de archivo.

## Principio

**Todo lo que se afirma, se pregunta y se responde sale del libro.** Cada respuesta lleva una
frase literal, citada entre «…», con su ubicación. Una cita que existe no basta: debe probar
*toda* la respuesta, y ninguna alternativa incorrecta puede ser defendible. Si algo no está
en el texto, no se pregunta y no se escribe.

`SKILL_DIR` = la carpeta donde está este archivo; los scripts están en `SKILL_DIR/scripts/`.
Ejecútalos con `python -I <ruta>`. Requisitos: `pip install pymupdf pillow numpy reportlab`,
y Tesseract solo si el libro está escaneado.

**Lee `references/flujo-completo.md` antes de empezar.** Tiene el detalle de cada paso y el
formato exacto de la guía. Los encargos de los subagentes están en
`references/prompts-subagentes.md`.

## Paso 0: encontrar el libro

Mira la carpeta de trabajo. Un archivo «libro» es un PDF, EPUB, DOCX, TXT, HTML, ODT, MOBI…
que **no** sea un entregable tuyo.

- **Un solo candidato:** úsalo sin preguntar.
- **Varios:** pregunta cuál, en una sola pregunta y con las opciones por nombre. No adivines.
- **Ninguno:** dilo y pide que deje el libro en la carpeta. No busques en Descargas ni en
  otras carpetas del usuario sin permiso.
- **Nunca sobrescribas** un archivo del usuario. Tus salidas van a `md/` y a archivos nuevos
  con nombre propio.

Averigua **qué quiere** y en qué orden, porque cambia el trabajo: ¿la guía, el resumen, o
ambos? ¿Para qué edad? ¿Cuántas preguntas? Si no lo dice, aplica los valores por defecto de
`flujo-completo.md` (guía completa para 10 años, 100 preguntas de alternativas) y **dilo en
el primer mensaje** para que pueda corregirte antes de que escribas 100 preguntas.

## Entregables

En la carpeta del proyecto, sin tocar el original:

| Archivo | Qué es | Obligatorio |
|---|---|---|
| `md/hoja_NNN.md` o `md/parte_NNN.md` | el texto extraído, una pieza por página o capítulo | sí |
| `md/_imagenes/pNNN.png` | imágenes de cada hoja (solo OCR), para revisar | solo OCR |
| `md/libro_completo.md` | todo el libro en orden, con cabecera | sí |
| `resumen.md` | resumen por capítulos o cuentos, con ubicación | si lo pidió |
| `cuestionario.md` | la guía de estudio con respuestas al final | sí |
| `resumen_vAAAA.MM.DD.HHMM.pdf` | el resumen para imprimir | si hay `resumen.md` |
| `cuestionario_vAAAA.MM.DD.HHMM.pdf` | la guía para imprimir | sí |
| `INFORME.md` | qué hiciste, qué quedó dudoso, cuántas preguntas | sí |

Nunca cambies el nombre del original ni lo muevas.

## Proceso

Cada paso tiene una condición que se debe cumplir para avanzar.

1. **Diagnostica y extrae.** Identifica el formato y saca el texto a `md/`. Si es un escaneo,
   OCR; si tiene texto, extracción directa. Mira 2 o 3 páginas de salida antes de seguir.
2. **Revisa el texto contra la fuente, hoja por hoja, sin excepciones.** Si viene de OCR,
   compara **todas** las hojas con su imagen original usando 4 o 5 subagentes en paralelo.
   El OCR pierde la última línea de una página y mete basura cerca de los dibujos *sin bajar
   su confianza*. En un libro digital, quita encabezados, pies y números sueltos y comprueba
   el orden de las columnas.
3. **Une y lee el libro completo** antes de escribir una sola línea. Sin haberlo leído no se
   resume ni se pregunta.
4. **Escribe el resumen** (si lo pidió): una sección por capítulo o cuento, sin inventar, con
   la ubicación al final de cada apartado. Toda frase entre «» debe ser literal.
5. **Escribe la guía:** primero la cita, después la pregunta y al final las alternativas.
   Estructura y formato exacto en `references/flujo-completo.md`.
6. **Verifica.** `verificar_citas.py` con 0 no encontradas y `verificar_clave.py` con 0
   errores. Después lanza **revisores independientes en contexto limpio** y **un lector a
   ciegas**. Si tu entorno no puede crear subagentes, dilo: una revisión hecha por ti mismo
   en la misma conversación no cuenta y no debe presentarse como si lo fuera.
7. **Genera los PDF versionados**, revisa 2 o 3 páginas como imagen, y escribe `INFORME.md`.
8. **Cierra con las lecciones** (ver Mantenimiento).

## Ubicación de las respuestas

- **Libro con páginas impresas:** `(pág. X)` es el número **impreso en el libro**, no el del
  archivo PDF. Calcula la equivalencia mirando 2 o 3 hojas y explícalo en la guía.
- **Libro sin páginas (EPUB, DOCX, TXT):** `(cap. N)`, con el número del capítulo **del
  libro**, no el de `parte_NNN`. Los títulos y datos impresos se comprueban en la imagen: a
  veces solo se ven por transparencia desde el reverso de la hoja.

## Señales de alerta: detente y corrige

| Pensamiento | Realidad |
|---|---|
| "Por el plazo, reviso solo las páginas dudosas del OCR" | Los errores más graves, como líneas perdidas, no aparecen como dudosos. Se revisan todas. |
| "La verificación automática de citas basta" | Solo prueba que la cita existe. No prueba que responda la pregunta ni que los distractores sean falsos. |
| "Que un adulto revise las preguntas" | La revisión es tu trabajo: revisores en contexto limpio y lector a ciegas. |
| "Reviso yo mismo, total es rápido" | Una revisión en el mismo contexto hereda tus errores. No es una revisión independiente. |
| "Resumo de memoria lo que entendí" | El resumen también se ancla al texto. Si no está en el libro, no va. |
| "Página 12" sin aclarar | ¿Del PDF o del libro? Siempre la del libro impreso, o el capítulo. |
| "Describo la ilustración y pregunto por ella" | Nunca se pregunta por ilustraciones: pueden estar mal interpretadas y a veces contradicen el texto. |
| "Hago las columnas del PDF con CSS o `fitz.Story`" | Usa `generar_pdf.py` (ReportLab). Chrome headless falla sin dar error cuando hay aislamiento. |
| "Guardo como guia.pdf" | Siempre con versión. Nunca se sobrescribe una versión anterior. |

## Errores frecuentes en las preguntas

- Una alternativa incorrecta se parece a algo que el personaje sí dijo.
- Un enunciado que regala la respuesta de otra pregunta, o dos preguntas con la misma respuesta.
- Palabras entre «» que el libro no dice tal cual. Las comillas «» se usan solo para texto del
  libro, y nunca en las alternativas.
- Un hecho que ocurre varias veces en "Ordena los hechos" sin precisar cuál.
- Palabras difíciles en las alternativas: simplifícalas para la edad.

## Mantenimiento

La skill mejora con cada libro, pero **un proyecto no edita la skill** mientras lo está
haciendo: eso mete datos de un libro en la herramienta de todos.

Al terminar cada libro:

1. Escribe `lecciones.md` **en la carpeta del proyecto**: qué falló, qué parámetro hubo que
   ajustar, qué tipo de error apareció. Con el ejemplo concreto.
2. Pregunta al usuario si quiere incorporarlas. Si dice sí, en una sesión aparte, en el
   repositorio de la skill: **generaliza** la lección (sin nombres, personajes ni páginas de
   ese libro), cámbiala en `references/flujo-completo.md` o en los scripts, y **ejecuta
   `python -I tests/run_tests.py`**. Si las pruebas fallan, la lección no entra.
3. Anota el cambio en `references/historial.md` y sube la versión de `VERSION`.
4. Avisa al usuario qué se agregó.

Reglas de esa sesión de mantenimiento: ver `AGENTS.md` del repositorio.
