# guia-estudio-desde-libro

**Skill para agentes de código** (Claude Code, Codex, OpenCode, Antigravity y otros
compatibles con el estándar *Agent Skills*). Deja un libro en una carpeta, pídeselo al agente,
y obtienes el texto completo, un resumen y una guía de estudio **verificada contra el texto**,
sin respuestas inventadas.

- Extrae el texto a Markdown desde PDF escaneado (con OCR), PDF con texto, EPUB, DOCX, TXT,
  HTML, ODT, MOBI y otros.
- Escribe un **resumen** por capítulos o cuentos, con la ubicación de cada apartado.
- Arma la **guía de estudio**: una sección con datos del libro y, en cada parte, preguntas de
  alternativas, *¿Quién lo dijo?*, ordenar hechos, verdadero o falso, vocabulario y preguntas
  para pensar.
- Cada respuesta lleva **la frase literal del libro** que la respalda y su página o capítulo.
- Verifica con scripts que cada cita esté en el libro y que la clave sea coherente, y además
  con revisores en contexto limpio y un lector a ciegas.
- Genera PDF para imprimir, A4 horizontal a 2 columnas, siempre con versión:
  `cuestionario_v2026.11.11.0930.pdf`.

## Cómo se usa

No hay comandos que recordar. En una carpeta vacía:

1. Instala la skill (abajo).
2. Deja el libro en la carpeta, por ejemplo `MiLibro.pdf`.
3. Pídeselo al agente en lenguaje natural:

> "Trabaja con el PDF de esta carpeta. Quiero el texto completo, un resumen y una guía de
> estudio de 100 preguntas para un niño de 10 años, con PDF para imprimir."

El agente deja esto, sin tocar tu archivo original:

```
MiLibro.pdf
md/libro_completo.md
resumen.md
resumen_v2026.11.11.0930.pdf
cuestionario.md
cuestionario_v2026.11.11.0932.pdf
INFORME.md          qué se hizo y qué quedó dudoso
```

## Instalación

El repositorio **es** la skill. El nombre de la carpeta de destino debe ser
`guia-estudio-desde-libro`, igual que el campo `name` de `SKILL.md`.

| Agente | Global (todos los proyectos) | Solo un proyecto |
|---|---|---|
| Claude Code | `~/.claude/skills/guia-estudio-desde-libro` | `.claude/skills/guia-estudio-desde-libro` |
| Codex CLI | `~/.codex/skills/guia-estudio-desde-libro` | `.agents/skills/guia-estudio-desde-libro` |
| OpenCode | `~/.config/opencode/skills/guia-estudio-desde-libro` | `.opencode/skills/guia-estudio-desde-libro` (también lee `.claude/skills` y `.agents/skills`) |

```bash
git clone https://github.com/edgardo001/skill-guia-estudio-desde-libro.git \
  ~/.claude/skills/guia-estudio-desde-libro
```

Para varios agentes, clona una vez y enlaza la carpeta en los demás. Así un `git pull` los
actualiza a todos.

```powershell
# Windows (PowerShell). La unión de directorios no requiere permisos de administrador.
git clone https://github.com/edgardo001/skill-guia-estudio-desde-libro.git "$HOME\.claude\skills\guia-estudio-desde-libro"
New-Item -ItemType Junction -Path "$HOME\.codex\skills\guia-estudio-desde-libro" -Target "$HOME\.claude\skills\guia-estudio-desde-libro"
```

```bash
# macOS / Linux
git clone https://github.com/edgardo001/skill-guia-estudio-desde-libro.git ~/.claude/skills/guia-estudio-desde-libro
ln -s ~/.claude/skills/guia-estudio-desde-libro ~/.codex/skills/guia-estudio-desde-libro
ln -s ~/.claude/skills/guia-estudio-desde-libro ~/.config/opencode/skills/guia-estudio-desde-libro
```

Las rutas cambian entre versiones de cada agente. Si no encuentra la skill, revisa su
documentación: [Claude Code](https://docs.claude.com/en/docs/claude-code/skills),
[Codex](https://developers.openai.com/codex/skills),
[OpenCode](https://opencode.ai/docs/skills).

### Alternativa universal (cualquier agente)

Si tu agente no soporta skills, agrega esto al `AGENTS.md` (o `CLAUDE.md`) del proyecto:

```markdown
Para extraer el texto de un libro o crear resúmenes y guías de estudio verificadas,
lee y sigue `<ruta-del-clon>/guia-estudio-desde-libro/SKILL.md` (SKILL_DIR = esa carpeta).
```

## Requisitos

- Python 3 y `pip install pymupdf pillow numpy reportlab`
- Solo para PDF escaneados: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) y el
  modelo de español. No viene en el repositorio (son 13 MB): el agente lo descarga en
  `tessdata/` **de tu proyecto** con `python -I scripts/obtener_tessdata.py`.
- Opcional: [pandoc](https://pandoc.org), para formatos poco comunes (ODT, RTF, DOC).

## Contenido

```
SKILL.md                          reglas y proceso (lo que lee el agente)
VERSION                           versión actual
AGENTS.md                         reglas para quien edite la skill
references/flujo-completo.md      detalle de cada paso y formato exacto de la guía
references/prompts-subagentes.md  encargos de corrección, revisores y lector a ciegas
references/historial.md           historial de cambios
scripts/                          extraer_libro, ocr_pdf, obtener_tessdata, unir_libro,
                                  verificar_citas, verificar_clave, generar_pdf
examples/                         plantillas ejecutables sobre un libro inventado
tests/run_tests.py                banco de pruebas (12 comprobaciones)
```

## Pruebas

```bash
python -I tests/run_tests.py
```

Genera una guía con el libro inventado de `examples/`, la pasa por los dos verificadores y
comprueba que **sí fallan** cuando se les pone un error a propósito. Corre en cada push
(`.github/workflows/pruebas.yml`).

## Mantenimiento

La skill mejora con cada libro, pero **un proyecto no edita la skill**. Al terminar, el agente
escribe `lecciones.md` en la carpeta del libro. Esas lecciones se incorporan después, en una
sesión aparte, generalizadas y con las pruebas en verde. Las reglas están en `AGENTS.md`.

Si instalaste la skill como clon, actualizar es:

```bash
cd ~/.claude/skills/guia-estudio-desde-libro && git pull
```

Para reproducir un proyecto antiguo, usa la versión con la que se hizo
(`git checkout v0.2.0`).

## Licencia

[MIT](LICENSE).
