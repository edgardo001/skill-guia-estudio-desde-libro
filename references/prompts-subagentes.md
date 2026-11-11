# Encargos para subagentes

Antes de usarlos, reemplaza los valores entre [corchetes]. Cada subagente parte sin contexto:
dale rutas absolutas.

**Contexto limpio, sin excepciones.** Un revisor tiene que llegar sin tu conversación, sin tus
razonamientos y sin tus dudas. Si el entorno no puede crear subagentes, no lo simules: dile al
usuario que la revisión independiente no se pudo hacer y no la presentes como hecha.

**Un foco por revisor.** Un revisor que mira todo a la vez no encuentra nada. Por eso son dos
revisores con focos distintos y no uno que revisa "la guía". Reparte por secciones, y dale a
cada uno el encargo que le corresponde.

Los informes van a `revision/<nombre>.md` en la carpeta del proyecto, no al chat. Tú los lees
desde el archivo.

---

## Corrección de transcripción (OCR), de 4 a 5 en paralelo, unas 10 hojas cada uno

> Para cada hoja N del rango [X]–[Y]: lee la imagen `[ruta]/md/_imagenes/pNNN.png` (trae [2]
> páginas del libro) y reescribe `[ruta]/md/hoja_NNN.md` como transcripción **fiel y completa**,
> palabra por palabra. Respeta las tildes, los signos ¡ ¿ y las rayas de diálogo (—).
> - Mantén los títulos `# Hoja N del PDF` y `## Página X`. Si se ve el número impreso de la
>   página, úsalo.
> - Pon un párrafo por línea, une las palabras cortadas con guion al final de línea y quita el
>   ruido: sellos, basura de las ilustraciones y números de página.
> - Si el texto rodea un dibujo, transcríbelo en el orden natural de lectura.
> - Incluye los títulos, la portada, el autor y la editorial.
> - Si una página no tiene texto, escribe `*(sin texto — ilustración)*`.
> - NO inventes: si algo no se lee, escribe `[ilegible]`. Si tienes dudas, recorta la imagen
>   con PIL para ampliarla.
> - No completes frases que siguen en otra hoja.
> - Al terminar, informa qué hojas tenían errores importantes y qué marcaste como `[ilegible]`.

---

## Revisor A — fidelidad y ubicación

Lee `[ruta]/cuestionario.md`, `[ruta]/md/libro_completo.md` y las imágenes
`[ruta]/md/_imagenes/pNNN.png` (la hoja N trae las páginas impresas [fórmula]; si el libro es
digital, no hay imágenes: usa los capítulos).

Tu único trabajo es comprobar que **lo que se afirma es verdad y está donde se dice**.

> Eres un revisor escéptico de una guía de estudio para niños de [edad] años. NO modifiques
> archivos. Escribe tu informe en `[ruta]/revision/revisor-a.md`.
> Alcance: [secciones o números de pregunta].
>
> Para cada ítem:
> 1. ¿La cita está en el libro y prueba **todo** lo que afirma la respuesta? Si la respuesta
>    dice dos cosas y la cita solo prueba una, es un problema.
> 2. ¿La ubicación es la correcta? Revisa al menos [8] páginas en imagen, o comprueba que el
>    capítulo indicado contenga la cita.
> 3. En "¿Quién lo dijo?", ¿el personaje es el que dice esa frase y no otro?
> 4. En "Ordena los hechos", ¿el orden de la respuesta es el que narra el libro? Si un hecho
>    ocurre más de una vez, ¿se precisa cuál?
> 5. En verdadero o falso, ¿la cita demuestra el valor asignado?
> 6. En vocabulario, ¿el significado corresponde al uso de la palabra **en esa frase**?
>
> Informa solo lo que está mal, con sección, número, qué falla, la cita y la ubicación que lo
> prueban, y la corrección. Al final, cuántos ítems revisaste y cuántos quedaron OK.
> No infles la lista con preferencias de estilo y no elogies: si no hay problemas, dilo en una
> línea.

---

## Revisor B — alternativas y ambigüedad

Lee `[ruta]/cuestionario.md` y `[ruta]/md/libro_completo.md`.

Tu único trabajo es la **pregunta como ejercicio**: que tenga una sola respuesta defendible.

> Eres un revisor escéptico de una guía de estudio para niños de [edad] años. NO modifiques
> archivos. Escribe tu informe en `[ruta]/revision/revisor-b.md`.
> Alcance: [secciones o números de pregunta].
>
> Para cada pregunta de alternativas:
> 1. ¿Alguna alternativa incorrecta es verdadera o defendible según el libro? Lee el contexto
>    de la cita, no solo la línea.
> 2. ¿Dos alternativas dicen lo mismo con otras palabras?
> 3. ¿El enunciado regala la respuesta de otra pregunta, o hay dos preguntas con la misma
>    respuesta?
> 4. ¿Se pregunta algo que el libro no dice, o sobre una ilustración?
> 5. ¿Las palabras son adecuadas para [edad] años? Nombra las que haya que simplificar.
> 6. ¿La respuesta marcada es realmente la mejor, y no solo la primera aceptable?
>
> Informa solo lo que está mal, con sección, número, qué falla y la corrección propuesta.
> Al final, cuántas preguntas revisaste y cuántas quedaron OK. No elogies.

---

## Lector a ciegas (1)

> Responde todas las preguntas de alternativas de `[ruta]/cuestionario.md` usando **solo**
> `[ruta]/md/libro_completo.md`. **No leas la sección "## Respuestas"** ni nada que venga
> después de ella. NO modifiques archivos. Escribe tus respuestas en
> `[ruta]/revision/lector-a-ciegas.md`.
> Para cada pregunta: sección, número, letra elegida, la frase del libro que la justifica y una
> marca `AMBIGUA` si dos alternativas podrían ser correctas o si ninguna lo es.
> Al final, lista aparte las preguntas marcadas como AMBIGUA y explica por qué.

Compara tú sus letras con la clave. **Cada diferencia es un problema tuyo, no del lector**:
o la pregunta es ambigua, o la clave está mal. Revisa las dos cosas.
