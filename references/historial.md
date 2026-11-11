# Historial de cambios de la skill

Anota aquí cada mejora: fecha, motivo, y el cambio en una línea. Las lecciones van en
`flujo-completo.md` o en `SKILL.md`, no aquí.

La versión vigente está en `VERSION`.

| Fecha | Versión | Motivo | Cambio |
|---|---|---|---|
| 2026-11-10 | 0.1.0 | libro inicial de prueba (PDF escaneado, 51 hojas) | Versión inicial: OCR con revisión hoja por hoja, guía con actividades A–F y citas verificadas, PDF A4 horizontal a 2 columnas. |
| 2026-11-10 | 0.1.0 | misma prueba | PDF siempre con versión (`_vAAAA.MM.DD.HHMM`). |
| 2026-11-10 | 0.1.0 | misma prueba | Revisión independiente obligatoria con subagentes; se documentan 5 tipos de error. |
| 2026-11-10 | 0.1.0 | misma prueba | Ampliación a 100 preguntas; la ubicación es la página del libro impreso y no la del PDF; 3 tipos de error más. |
| 2026-11-10 | 0.1.0 | auditoría | Se agregan `verificar_clave.py` y `unir_libro.py`, los ejemplos, las buenas prácticas (respaldos, UTF-8 con `python -I`, reemplazos con `assert`) y las preferencias del usuario. |
| 2026-11-10 | 0.1.0 | empaquetado | `extraer_libro.py` para PDF con texto (detecta columnas), EPUB, DOCX, TXT, HTML y otros formatos; ubicación `(cap. N)`; lector a ciegas; tabla de señales de alerta. |
| 2026-11-10 | 0.1.0 | estructura | El repositorio pasa a ser la skill misma (`SKILL.md` en la raíz): se instala con `git clone` directo en la carpeta de skills. |
| 2026-11-10 | 0.1.0 | prueba de uso | Novelas agrupadas en 3–4 partes (encabezados siempre `## Parte `); capítulos según el libro; OCR con hojas de distinto formato; los subagentes de corrección sí editan; rondas de revisión; plazos. |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Skill genérica:** se eliminan los datos del libro de prueba. Los ejemplos pasan a un libro inventado (`examples/libro_ejemplo.md`) y se reescriben como plantillas ejecutables (`plantilla_guia.py`, `ampliar_alternativas.py`). |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Flujo por carpeta:** la skill descubre el libro en la carpeta de trabajo, no pide comandos, y entrega un juego fijo de archivos (`md/libro_completo.md`, `resumen.md`, `cuestionario.md`, PDFs, `INFORME.md`). |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Nuevo entregable: `resumen.md`**, con la misma regla de cero invenciones y ubicación por apartado. |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Banco de pruebas** (`tests/run_tests.py`) con 12 comprobaciones sobre el libro inventado, incluidas pruebas negativas; CI en GitHub Actions. |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Mantenimiento en dos repos:** cada proyecto escribe `lecciones.md` y no edita la skill; las lecciones se generalizan en una sesión aparte, con pruebas. Reglas en `AGENTS.md`, versión en `VERSION`. |
| 2026-11-11 | 0.2.0 | publicación en GitHub | **Revisores con foco único** (A: fidelidad y ubicación; B: alternativas y ambigüedad), informes en `revision/*.md`, y la regla de que sin subagentes no hay revisión independiente. |
| 2026-11-11 | 0.2.0 | publicación en GitHub | Licencia MIT (`LICENSE`). |
| 2026-11-11 | 0.2.0 | publicación en GitHub | El modelo de español de Tesseract (13 MB) sale del repositorio: `obtener_tessdata.py` lo descarga en `./tessdata` del **proyecto**, y `ocr_pdf.py` lo busca ahí, en `TESSDATA_PREFIX` y en la instalación de Tesseract. |
