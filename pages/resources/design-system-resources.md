# Resources Page — Sub Design System

Clases específicas de la página `/resources`. Complementan el design system global (`/design-system.md`).

---

## Estructura de la página

Dos secciones únicamente:

1. **Intro** — título H1 + subtítulo + featured card horizontal.
2. **Grid** — 3 columnas x 2 filas de resource cards (6 cards).

---

## Sección Intro

### `.section--resources-hero`
Modifier de `.section`. Padding-top extra para dejar espacio bajo el navbar fijo.
- `padding-top: 12em`

### `.hero-resources-header`
Contenedor del título + subtítulo.
- `display: flex; flex-direction: column; gap: 1.2em`
- `max-width: 40em`

---

## Featured Card (horizontal)

No es un componente reutilizable — vive solo en esta página. Layout horizontal: imagen a la izquierda, contenido a la derecha.

### `.card--resource-featured`
- `display: flex; flex-direction: row; gap: 2.5em`

### `.card-resource-featured-image`
Placeholder de imagen (fondo `--color-placeholder: #E3E3E3`).
- `flex: 0 0 42%`
- `min-height: 22em`
- `border-radius: 0.5em`

### `.card-resource-featured-content`
- `flex: 1 1 auto`
- `display: flex; flex-direction: column; justify-content: center; gap: 1em`

### `.card-resource-date`
Fecha compartida entre featured card y grid cards. `font-weight: 600`.

### `.card-resource-featured-title`
Título de la featured card. `font-size: 2em; font-weight: 600`.

### `.card-resource-featured-desc`
Descripción. `color: rgba(16,16,16,0.65)`.

Botón: `.btn.btn-purple` ("Read article").

---

## Grid de Resource Cards

### `.section--resources-grid`
Modifier de `.section` sin padding-top (pegado a la sección anterior).

### `.resources-grid`
- `display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.5em`
- Mobile: 1 columna.

### `.card--resource`
Card vertical (imagen arriba, contenido abajo). No usa la clase base `.card` del design system global porque no requiere overflow hidden en toda la card (solo en la imagen).
- `display: flex; flex-direction: column; gap: 1.2em`

### `.card-resource-image`
Placeholder de imagen, `aspect-ratio: 1.2 / 1`, fondo `--color-placeholder`.

### `.card-resource-body`
- `display: flex; flex-direction: column; gap: 0.85em`

### `.card-resource-title`
`font-size: 1.43em; font-weight: 600`.

### `.card-resource-desc`
`color: rgba(16,16,16,0.65)`.

Botón: `.btn.btn-purple` ("View Article").

---

## Notas

- Los tamaños de imagen son placeholders (`--color-placeholder: #E3E3E3`) hasta tener assets reales del cliente — reemplazar el `div` por un `<img>` o `background-image` cuando se conecte al CMS.
- Navbar y footer son los componentes globales importados sin modificaciones (`/components/navbar/`, `/components/footer/`).
- Todos los tamaños de texto en mobile van en `px` fijos, siguiendo la regla global del design system.
