# AGENTS.md — reglas para mantener esta skill

Este repositorio **es** la skill. Cualquier agente que la edite cumple estas reglas.

## Qué es y qué no es

- Es una **herramienta genérica**. Sirve para cualquier libro.
- **No** guarda datos de ningún libro concreto: ni títulos, ni personajes, ni citas, ni
  páginas, ni preguntas reales. Ni en `SKILL.md`, ni en `references/`, ni en `examples/`.
- Los ejemplos usan el libro inventado `examples/libro_ejemplo.md`.

Si una lección solo tiene sentido para un libro, **no entra en la skill**. Entra el patrón.

## Antes de cambiar algo

```bash
python -I tests/run_tests.py        # debe dar "12/12 pruebas OK"
```

Después del cambio, vuelve a ejecutarlo. **Si las pruebas fallan, no se sube.**

Si agregas un comportamiento nuevo, agrega su prueba en `tests/run_tests.py`. Un
verificador que nunca falla no verifica nada: cada regla nueva necesita una prueba que
compruebe que se cumple y otra que compruebe que se detecta cuando se rompe.

## Cómo entra una lección nueva

1. La lección se anota primero en `lecciones.md` del **proyecto del libro**, con el caso
   concreto que la provocó.
2. En este repositorio se **generaliza**: se describe el patrón, sin datos de ese libro.
3. Va en el lugar que corresponde, no al final de todo:
   - una regla de trabajo o una señal de alerta → `SKILL.md`;
   - el detalle de un paso o del formato → `references/flujo-completo.md`;
   - un encargo de subagente → `references/prompts-subagentes.md`;
   - algo que pueden hacer todos los libros → el script correspondiente.
4. Se anota en `references/historial.md` (fecha, motivo, cambio en una línea).
5. Si cambia el comportamiento, sube `VERSION` (`MAYOR.MENOR.PARCHE`):
   - MAYOR: cambia el formato de la guía o el uso de los scripts;
   - MENOR: una regla o capacidad nueva;
   - PARCHE: redacción, ejemplos, correcciones.

## Prohibido

- Meter el nombre, el autor o las citas de un libro real en los archivos de la skill.
- Dejar un ejemplo que no se pueda ejecutar (`examples/` debe funcionar tal cual).
- Cambiar el formato que leen `verificar_clave.py` y `generar_pdf.py` sin cambiar los dos
  scripts y sus pruebas.
- Subir un PDF, un libro o cualquier obra de terceros al repositorio.

## Estilo

- En español, con tildes y signos ¡ ¿ correctos.
- Frases cortas. Tablas para lo que se compara, listas para lo que se hace.
- UTF-8 en todos los archivos. En Windows, los scripts fuerzan
  `sys.stdout.reconfigure(encoding="utf-8")`.

## Licencia

Todo lo que se agregue queda bajo la licencia del repositorio (ver `LICENSE`).
