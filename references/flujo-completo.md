# Flujo completo: de libro a guía de estudio verificada

Detalle de los pasos de `SKILL.md`. `S` = `SKILL_DIR/scripts`. Trabaja en la carpeta del usuario, donde está el libro. Responde en el idioma del usuario; en español, con tildes y signos ¡ ¿ correctos.

Estructura de salida en la carpeta del usuario:

```
LIBRO.ext                              el original: no se mueve ni se cambia
md/
  hoja_NNN.md  (OCR)  o  parte_NNN.md  (extraer_libro.py)
  _imagenes/pNNN.png   (solo OCR: imágenes de cada hoja, para revisar)
  libro_completo.md
resumen.md                             si lo pidió
resumen_vAAAA.MM.DD.HHMM.pdf           uno nuevo por cada generación
cuestionario.md
cuestionario_vAAAA.MM.DD.HHMM.pdf      uno nuevo por cada generación
INFORME.md                             qué se hizo y qué quedó dudoso
```

Los nombres son siempre estos. No los cambies según el libro: así el usuario encuentra lo mismo en todos sus proyectos.

Buenas prácticas:
- **Respalda antes de editar con scripts:** copia el archivo, por ejemplo `cuestionario_backupN.md`, al scratchpad o a la carpeta temporal.
- **Reemplazos en Markdown:** usa `str.replace` con un `assert` del número de coincidencias, no `sed` ni regex frágiles. Para encabezados, busca con salto de línea delante (`"\n## Parte I: "`), porque `"## Parte I"` también coincide dentro de `"### Parte I"` y de `"## Parte II"`.
- **Consola de Windows:** `python -I` ignora `PYTHONIOENCODING`. Los scripts de la skill fuerzan UTF-8; hazlo también en los scripts nuevos (`sys.stdout.reconfigure(encoding="utf-8")`).

---

## 1. Diagnóstico y extracción

```bash
python -I S/extraer_libro.py LIBRO.ext md [--primera-pagina N]
```

| Formato | Qué hace | Cómo se ubican las respuestas |
|---|---|---|
| PDF con texto | Una parte por página, ordenada por bloques. Detecta 2 columnas o 2 páginas por hoja. | `(pág. X)` impresa. Usa `--primera-pagina` con el número impreso de la página 1 del PDF. |
| PDF escaneado | Lo detecta y se detiene: usa `ocr_pdf.py`. | `(pág. X)` impresa. |
| EPUB | Una parte por capítulo, en el orden del spine. | `(cap. N)` |
| DOCX | Una parte por cada título de nivel 1. | `(cap. N)` |
| TXT, MD, HTML | Una sola parte; divídela tú en `## Capítulo N: título`. | `(cap. N)` |
| ODT, RTF, DOC, MOBI, FB2… | pandoc si está instalado; si no, PyMuPDF. | `(cap. N)` |

- **Un PDF mixto** (texto con algunas páginas de imagen): el script avisa qué páginas no tienen texto. Míralas en imagen; si traen texto, haz OCR solo de ellas.
- **Mira siempre 2 o 3 páginas o capítulos** para confirmar el orden de lectura, los encabezados repetidos y la numeración.
- **Libro con dibujos:** renderiza una hoja con `page.get_pixmap(dpi=300)` y mírala.

### OCR (solo PDF escaneado)

```bash
python -I S/ocr_pdf.py LIBRO.pdf md --paginas-por-hoja 2 --primera-pagina N
```

- `--primera-pagina` es el número impreso de la página izquierda de la hoja 1. Confírmalo mirando los números impresos de 2 o 3 hojas. Por ejemplo, la hoja *n* puede tener las páginas 2n+4 y 2n+5.
- El script blanquea los píxeles con color saturado (`S > 70` en HSV), es decir, las ilustraciones, y mantiene el gris del texto. Binarizar en blanco y negro adelgaza demasiado la letra.
- **Falta el modelo de español de Tesseract:** `ocr_pdf.py` lo busca solo (en `--tessdata`, en
  `./tessdata` de la carpeta actual, en `TESSDATA_PREFIX` y en la carpeta de Tesseract). Si no
  está, `obtener_tessdata.py` lo descarga en **`./tessdata` del proyecto** (13 MB, una vez):
  la skill nunca guarda binarios. Recuérdale al usuario agregar `tessdata/` al `.gitignore`
  de su proyecto.
- Si los encabezados o pies están a otra altura, ajusta `top=0.165` y `bottom=0.86` en `to_paragraphs`.
- **Hojas con formato distinto** (portada suelta, hojas con 1 página y otras con 2): separa el PDF en tramos con PyMuPDF (`insert_pdf(from_page, to_page)`) y ejecuta el OCR de cada tramo con su propio `--paginas-por-hoja` y `--primera-pagina`. También puedes dejar `--primera-pagina` sin indicar y hacer que los subagentes de corrección pongan el número impreso que ven en cada página.
- Imágenes: `md/_imagenes/pNNN.png` es la hoja original, la que se usa para revisar. `pNNN_0.png` y `pNNN_1.png` son mitades sin color que solo usa el OCR.
- El resultado es solo un borrador. Las páginas de puro texto salen casi perfectas. En las que tienen texto alrededor de un dibujo, el OCR **mete basura y pierde la última línea**.

## 2. Revisión contra la fuente (obligatoria y completa)

- **OCR:** reparte todas las hojas entre 4 o 5 subagentes en paralelo, unas 10 hojas cada uno. Usa el encargo "Corrección de transcripción" de `prompts-subagentes.md`.
- **Texto digital:** revísalo tú mismo. Quita encabezados y pies repetidos, números de página sueltos y notas de copyright. Comprueba que las columnas estén en orden y que los capítulos estén bien cortados.
- **EPUB, DOCX y otros libros sin páginas:** `extraer_libro.py` escribe `## Capítulo N: título` en cada parte, pero N es el orden del archivo. Borra o junta las partes que no son capítulos (portada, dedicatoria, índice, créditos), renumera los archivos y **corrige a mano** cada `## Capítulo N` para que tenga el número del libro. Si los capítulos no tienen número, deja su título; la ubicación será `(cap. «Título»)`.
- **Separadores de escena:** escríbelos `\* \* \*`, porque `* * *` se convierte en una línea horizontal en Markdown.
- **Ilustraciones:** se describen solo como `*(Ilustración: …)*`. Pueden estar mal interpretadas; por ejemplo, un subagente puede confundir a un personaje secundario con el protagonista. Revísalas y **nunca las uses para preguntas**.

## 3. Unir y leer

```bash
python -I S/unir_libro.py md "Título" "Autor" "Colección, Editorial" "I. Cuento (págs. 9–40)" "II. …"
```

Para una novela sin páginas: `"Capítulos 1–12"`, o `"1. Título (cap. 1)" "2. …"`.

Vuelve a unir cada vez que corrijas una parte. Lee el libro completo antes de escribir preguntas.

## 4. El resumen (`resumen.md`)

Solo si lo pidió. Va antes de la guía, porque resumir obliga a ordenar la historia y eso
mejora las preguntas.

- Una sección por cuento o capítulo, con el mismo título que usa el libro.
- Cuenta lo que pasa **sin inventar nada**: ni hechos, ni motivaciones, ni detalles que el
  texto no diga. Si una idea no se puede sostener con una frase del libro, no va.
- Cada apartado termina con su ubicación: `(págs. 9–14)` o `(cap. 3)`.
- Las citas textuales, entre «», siguen la misma regla que la guía:
  `python -I S/verificar_citas.py resumen.md md/libro_completo.md`.
- Extensión: entre un cuarto y un tercio del original. Un cuento de 6 páginas no se resume
  en 4.
- Cierra con dos o tres líneas sobre los temas del libro, sin sermonear.

## 5. La guía (`cuestionario.md`)

Es material **para aprender**: la prueba la hace el profesor o la profesora. No lleva puntaje ni nota. El lenguaje debe servir para la edad indicada; por defecto, 10 años.

Preferencias por defecto del usuario (mantenlas salvo que pida otra cosa):
- Separada por las secciones del libro (cuentos o capítulos), y cada sección se numera desde 1.
- Una sección inicial con datos generales.
- **100 preguntas de alternativas** en total, **contando las de la sección inicial**. Las actividades B–F van aparte.
- Respuestas al final, con cita y ubicación.
- PDF A4 horizontal a 2 columnas, con versión.
- Si no se puede llegar a 100 sin inventar, entrega menos y avisa.

Según el tipo de libro:
- **Libro de cuentos:** una `## Parte N: <título del cuento>` por cuento. Al final va `## Para pensar en los N cuentos`.
- **Novela o libro por capítulos:** agrupa los capítulos en 3 o 4 partes según los grandes momentos de la historia, por ejemplo `## Parte I: Capítulos 1–4`. Cada parte lleva las actividades A–F y las preguntas de A se reparten según el largo. Al final va `## Para pensar en todo el libro`.
- **Los encabezados siempre empiezan con `## Parte `**, aunque sean capítulos, porque así los reconocen `verificar_clave.py` y `generar_pdf.py`. Tampoco uses `## Capítulo` dentro de `cuestionario.md`.

Edad: las preguntas y las alternativas se escriben con palabras que entienda el niño de la edad indicada, aunque el libro use otras más difíciles. **La cita se deja literal**, sin cambios. Si el libro es de un nivel mucho más alto que la edad, avisa al usuario.

Estructura (el formato exacto lo leen `verificar_clave.py` y `generar_pdf.py`):

```markdown
# Guía de estudio
## *Título* — Autor
**Nombre:** ______________________________
### ¿Cómo usar esta guía?
1. Lee primero el cuento completo. 2. Responde sin mirar el libro. 3. Revisa en Respuestas. 4. Si te equivocaste, busca la página y lee la frase.
**Importante:** las páginas indicadas son las del libro impreso, no las del archivo PDF.
   ← Novela o libro sin páginas: "1. Lee primero los capítulos de esa parte. … 4. Si te equivocaste, busca el capítulo indicado y lee la frase."
      y "**Importante:** junto a cada respuesta se indica el capítulo del libro donde está."
---
## Sección inicial: Sobre el libro          ← autor, editorial, colección, nº de cuentos, títulos, premios impresos
### Elige la alternativa correcta
**1. ¿Pregunta?**

- a) …
- b) …
- c) …
- d) …

## Parte I: <título del cuento>
### A. Elige la alternativa correcta      ← preguntas literales; las incorrectas deben ser creíbles, idealmente del mismo cuento
### B. ¿Quién lo dijo?                    ← 5–6 citas; "Elige entre: *personaje*, *personaje*." ; «cita» Lo dijo: ________
### C. Ordena los hechos                  ← 5 hechos: "- ( ) hecho"
### D. ¿Verdadero o falso?                ← 5 afirmaciones: "1. ( ) afirmación" (las falsas cambian un detalle del texto)
### E. Aprende palabras nuevas            ← 3 palabras dentro de su frase del libro, con 4 significados
### F. Piensa y responde                  ← 3 preguntas de "por qué" que el libro responde de forma explícita, más 1 de opinión
## Para pensar en los tres cuentos        ← 2–3 preguntas abiertas que relacionen los cuentos
---
## Respuestas
### Sección inicial: Sobre el libro
1. **a) texto exacto de la alternativa** — *«cita literal»* (Portada)
### Parte I: <mismo título>
**A. Alternativas**
1. **c) texto exacto** — *«cita literal»* (pág. 9)        ← o (cap. 2); "págs." si son varias páginas
**B. ¿Quién lo dijo?**
1. El personaje (pág. 11)
**C. Orden de los hechos**
1. hecho … 5. hecho
**D. Verdadero o falso**
1. **V** — *«cita»* (pág. 12)
**E. Palabras nuevas**
1. **b) significado**
**F. Piensa y responde**
1. Idea de respuesta. *«cita»* (pág. 15)      ← en las de opinión: "Respuesta personal. Pista: …"
```

Para ver un generador completo, ejecuta `examples/plantilla_guia.py` con
`examples/ejemplo_datos.json` y `examples/libro_ejemplo.md`. Guarda la estructura de los datos
(pregunta, alternativas, cita, ubicación), equilibra las letras y verifica las citas antes de
escribir.

Reglas de calidad:
- Escribe **primero la cita**, luego la pregunta y al final las alternativas.
- Equilibra las letras correctas en toda la guía: aproximadamente la misma cantidad de a, b, c y d. Asígnalas con una semilla fija.
- «…» se usa **solo** para texto literal del libro. Las alternativas incorrectas nunca van entre «».
- Al citar un diálogo, la palabra citada debe ser la que el libro dice a ese personaje. Por ejemplo, el libro dice «¡Mientes!»; no escribas «mentiroso» si nadie lo dice así.
- "pág." para una página, "págs." para varias. Si la frase empieza en una página y sigue en la otra, indica ambas.
- Los títulos y números de capítulo impresos se comprueban en la imagen. A veces solo se ven por transparencia desde el reverso de la hoja.
- Si una ilustración contradice el texto, no preguntes por ese detalle. Por ejemplo, el texto dice "vestido de negro" y el dibujo lo muestra de azul.

Errores que encontraron los revisores (evítalos desde el principio):
- **Hechos que ocurren varias veces** en "Ordena los hechos": precisa cuál ("Durante la fiesta, …").
- **Distractores casi verdaderos**, parecidos a algo que el personaje sí dijo: cámbialos por uno claramente falso.
- **Citas que respaldan solo una parte** de la respuesta: alárgalas o cambia la cita.
- **Un enunciado que regala la respuesta de otra pregunta**, o dos preguntas con la misma respuesta.
- **Palabras difíciles en las alternativas** ("atisbo", "estela"): simplifícalas o explícalas ("carromato (un carro grande)").

### Ampliar una guía

- Agrega las preguntas nuevas **al final de la actividad A** de cada parte, sin renumerar las anteriores. Sus respuestas van al final del bloque "A. Alternativas".
- Repártelas según el largo de cada sección. La sección inicial crece solo si el libro tiene más datos impresos.
- Revisa que las nuevas no repitan nada de las actividades A–F.
- Asigna las letras de las nuevas de modo que el **total** quede equilibrado.
- Para ver cómo se hace, ejecuta `examples/ampliar_alternativas.py` con `examples/ejemplo_ampliacion.json`: elige las letras para equilibrar el total y verifica las citas antes de escribir.
- Repite el ciclo completo de verificación (paso 6), con los revisores enfocados solo en las preguntas nuevas.

## 6. Verificación (obligatoria)

```bash
python -I S/verificar_citas.py cuestionario.md md/libro_completo.md   # 0 no encontradas
python -I S/verificar_clave.py cuestionario.md                        # Errores: 0
```

Después, en contexto limpio y en paralelo (encargos en `prompts-subagentes.md`):
1. **Revisor A, fidelidad y ubicación:** que la cita pruebe toda la respuesta, que la página o el capítulo sean los correctos, y que B, C, D y E estén bien.
2. **Revisor B, alternativas y ambigüedad:** que ningún distractor sea defendible, que no haya dos preguntas con la misma respuesta, que un enunciado no regale la respuesta de otra, y que el lenguaje sirva para la edad.
3. **Lector a ciegas:** responde todas las preguntas de alternativas solo con `libro_completo.md`, sin ver la sección Respuestas. Cada diferencia con la clave es una pregunta ambigua o una clave mal puesta.

Los subagentes **solo informan**, en `revision/*.md`. Las correcciones las aplicas tú, y después vuelves a ejecutar los dos verificadores.

**Si no puedes crear subagentes**, no hay revisión independiente: dilo en `INFORME.md` y en el mensaje final. No la sustituyas por tu propia relectura.

- **Si revisores y lector no coinciden:** decide tú mirando la fuente, el texto y la imagen de esa página. Si queda en duda, cambia la pregunta por otra que no se pueda discutir.
- **Cuántas rondas:** una de revisión completa. Si después de corregir cambiaste más de 5 ítems, haz una segunda ronda solo sobre esos ítems.
- La única excepción a "solo informan" son los subagentes de **corrección de transcripción** del paso 2, que sí editan su `hoja_NNN.md`.

## 7. PDF

```bash
python -I S/generar_pdf.py cuestionario.md      # -> cuestionario_v2026.11.10.1640.pdf
```

- Genera un A4 horizontal a 2 columnas, con línea divisoria y número de página.
- Cada pregunta queda junto a sus alternativas, y ningún título queda solo al final de una columna.
- `## Respuestas` empieza en una página nueva, con letra un poco más chica.
- Siempre crea el archivo con versión, `_vAAAA.MM.DD.HHMM`, y agrega `_2`, `_3`… si ya existe uno de ese minuto. Nunca sobrescribe.
- Usa ReportLab con fuente Georgia (o Arial o DejaVu si no está). Georgia no tiene "→", que sale como ☐; escribe en su lugar "Lo dijo: ____".
- Revisa el resultado: convierte 2 o 3 páginas a PNG con PyMuPDF y míralas. Confirma también que las tildes y los signos se vean bien.
- Chrome o Edge en modo headless no sirven: en entornos con aislamiento no generan el PDF y terminan sin error.

## 8. Entrega

- [ ] Texto revisado contra la fuente y `libro_completo.md`.
- [ ] `resumen.md`, si lo pidió: sin hechos inventados, con ubicación en cada apartado y sus citas verificadas.
- [ ] `cuestionario.md` con la sección inicial, partes A–F, las preguntas finales y las respuestas con cita y ubicación.
- [ ] `verificar_citas.py` con 0, `verificar_clave.py` con 0 errores y letras equilibradas.
- [ ] Revisores en contexto limpio y lector a ciegas hechos, y sus hallazgos corregidos.
- [ ] PDF con versión generado y revisado visualmente (uno por cada `.md` entregado).
- [ ] `INFORME.md`: qué se corrigió, qué quedó dudoso, cuántas preguntas tiene cada sección y los nombres exactos de los PDF.
- [ ] `lecciones.md` en la carpeta del proyecto (no en la skill).
