# The EdTech Mentor Page — Sub Design System

Clases específicas de la página `/edtech-mentor`. Complementan el design system global (`/design-system.md`).

---

## Componentes globales usados

- **Navbar** — `/components/navbar/` (`navbar.css` + `navbar.js`). Variante inicial: `nav--white`.
- **Footer** — `/components/footer/` (`footer.css`).

Ver `/components/design-system-components.md` para el detalle de clases de ambos componentes (`.nav`, `.btn-nav`, `.footer`, etc.).

---

## Sección Hero / Intro

### `.section--hero`
Modifier de `.section`. Padding reducido respecto al default (no es un hero full-height, es un intro corto de página interna).
- `padding-top: 9em` — `padding-bottom: 2.5em`

### `.hero-container`
Modifier de `.container`. Gap reducido entre breadcrumb, H1 y subtítulo.
- `gap: var(--space-xs)`

### `.section--hero h1`
Override tipográfico del H1 global para esta sección (headline en Lora, no Inter).
- Lora, `font-weight: 500`, `font-style: normal`, `2.9em`, line-height 1.25, letter-spacing `-0.34px`

### `.breadcrumb`
Contenedor flex del breadcrumb superior (`Home > EdTech Mentor Interviews.`).
- Inter, 400, `1em`, `opacity: 0.55` para look muted
- `margin-bottom: var(--space-xs)` para separarlo del H1

### `.breadcrumb-link`
El link "Home" dentro del breadcrumb. Subrayado, hereda color del padre.
- Hover: `--color-indigo`

### `.breadcrumb-current`
Texto plano del breadcrumb (página actual), sin link.

---

## Sección Pills (filtros)

### `.section--pills`
Modifier de `.section`. Pegado al hero, sin padding-top.
- `padding-top: 0` — `padding-bottom: var(--space-lg)`

### `.pills-wrap`
Contenedor flex con wrap para las 4 pills.

### `.pill`
Pill base outline (mismo patrón visual que `/work`). Usado para los 3 filtros: `Essencial`, `Investor`, `Founders`.
- `data-filter` = ID de la sección ancla correspondiente (`essencial`, `investor`, `founders`)
- Al hacer click: scroll suave hacia la sección con ese ID (ver `script.js`)

### `.pill--subscribe`
Modifier de `.pill`. Pill fija (no es un filtro) para el link "Subscribe on LinkedIn".
- Fondo y borde: `--color-purple` — Texto: `--color-black`
- Es un `<a target="_blank">` real hacia LinkedIn, sin `data-filter` — el JS del filtro la ignora

---

## Featured Card

Componente reutilizado tal cual desde `/components/featured-card` (requiere también `/components/work-card/work-card.css` por la clase base `.card`). Markup y contenido placeholder (Julie Kelleher / Kelleher Consulting Group) idénticos a los usados en `/home`.

**Importado en `<head>`:**
- `/components/work-card/work-card.css`
- `/components/featured-card/featured-card.css`

### `.section--featured-mentor`
Modifier de `.section`. Sin padding-top para quedar pegada a la sección de pills.

### `.featured-mentor-wrap`
Wrapper que define el tamaño real de `.card--featured` (que es `width/height: 100%`).
- Desktop: `height: 43.93em` (615px @ 14px base)
- Mobile (`≤768px`): `height: 35.56em` (320px @ 9px base)
- `overflow: hidden` para garantizar que el wrapper nunca exceda esa altura, incluso considerando que el componente `featured-card` trae su propio override `height: auto !important` en su media query mobile (pensado para el caso de `/home`, donde la card crece libremente). En esta página el wrapper fuerza el alto fijo en ambos breakpoints y recorta cualquier contenido que se pase.

---

## Sección "Essential series" (`#essencial`)

Fondo indigo (duplica el patrón visual de `.section--mentor-home` en `/home`). Contiene intro (título + subtítulo + 2 botones) y, debajo, un `cards-slider` sin título con cards `edtech-mentor-card`.

**Importado en `<head>`:**
- `/components/edtech-mentor-card/edtech-mentor-card.css`
- `/components/cards-slider/cards-slider.css` (además de `work-card.css`, ya importado para el featured card)
- `/components/cards-slider/cards-slider.js` al final del `<body>` (auto-inicializa cualquier `.slider-block` de la página)

### `.section--essential-mentor`
Modifier de `.section`. Fondo `--color-indigo`, texto `--color-white` por default (heredado por hijos como `.text-body--sm`).
- `padding-top: 6.86em` — `padding-bottom: 6.86em` (96px @ 14px base)

### `.essential-mentor-container`
Modifier de `.container`. Sin restricción de ancho (el H2 hace wrap natural con el `max-width` del `.container` base).

### `.section--essential-mentor h2`
Override tipográfico scoped (mismo patrón que `.section--mentor-home h2` en `/home`).
- Lora, 500, `2.57em`, line-height 1.25, letter-spacing `-0.36px`

### `.inter-accent` (dentro del h2)
Span que cambia la segunda parte del título a Inter (sans), manteniendo el resto en Lora.

### `.essential-mentor-actions`
Fila flex de los 2 botones (`Go to Series` — placeholder `href="#"` — y `Subscribe on LinkedIn` — link real a LinkedIn).
- Mobile (`≤768px`): `flex-direction: column; align-items: baseline;`

### `.section--essential-mentor .btn-white`
Override scoped de la variante global `.btn-white`: sobre fondo indigo, fondo y borde blancos sólidos, texto `--color-indigo`. Hover: fondo transparente, borde y texto blancos.

### `.section--essential-mentor .slider-arrow`
Override scoped del `cards-slider`: outline blanco sobre indigo (en vez del negro default). Hover: fondo blanco, ícono negro.

### `.section--essential-mentor .sliders-container`
- `padding-top: 7.14em` (100px @ 14px base)

### Slider de esta sección
Usa `.sliders-container` (mismo nombre que en `/home`) para el spacing, `.slider-block` **sin** `.slider-header` (sin título, según lo pedido), y 6 `card--edtech-mentor` con contenido placeholder (Julie Kelleher / Kelleher Consulting Group — mismo placeholder que el featured card y que `/home`).

---

---

## Sección "Investor series" (`#investor`)

Copia exacta de la estructura de `#essencial` (mismo `.container` + `.sliders-container` + `.slider-block` sin título, mismas 6 `edtech-mentor-card`), con su propia paleta:

### `.section--investor-mentor`
- Fondo `--color-purple`, texto `--color-black`
- `padding-top`/`padding-bottom: 6.86em` (96px @ 14px base)

### `.investor-mentor-container` / `.investor-mentor-actions`
Mismos nombres que en Essential pero con el prefijo `investor-`. `.investor-mentor-actions` en mobile: `flex-direction: column; align-items: baseline;` (igual que Essential).

### `.section--investor-mentor .btn-white`
Fondo/borde negro, texto blanco. Hover: fondo transparente, borde negro, texto negro.

### `.section--investor-mentor .card-edtech-mentor-role` / `.card-edtech-mentor-name`
Override a `--color-black` (el componente los trae blancos por default, pensado para fondos oscuros/indigo).

### `.section--investor-mentor .slider-arrow`
Outline negro (coincide con el default del componente, pero se declara explícito para este contexto). Hover: fondo negro, ícono blanco.

### `.section--investor-mentor .sliders-container`
`padding-top: 7.14em` (100px @ 14px base)

**Título:** `Investor Series <span class="inter-accent">Interviews</span>` — **Subtítulo:** "The Impact of Investment in EdTech, hosted by Phill Miller"

---

## Sección "Founders series" (`#founders`)

Misma copia exacta, con su propia paleta:

### `.section--founders-mentor`
- Fondo `--color-black` (#101010), texto `--color-white`
- `padding-top`/`padding-bottom: 6.86em` (96px @ 14px base)

### `.founders-mentor-container` / `.founders-mentor-actions`
Mismos nombres que en Essential pero con el prefijo `founders-`. `.founders-mentor-actions` en mobile: `flex-direction: column; align-items: baseline;`

### `.section--founders-mentor .btn-white`
Mismos colores que en Essential series: fondo/borde blanco, texto indigo. Hover: fondo transparente, borde y texto blancos.

### `.section--founders-mentor .slider-arrow`
Outline blanco. Hover: fondo blanco, ícono negro. (No hace falta override de `card-edtech-mentor-role`/`name`: el default blanco del componente ya funciona sobre este fondo oscuro.)

### `.section--founders-mentor .sliders-container`
`padding-top: 7.14em` (100px @ 14px base)

**Título:** `Founders Series <span class="inter-accent">Interviews</span>` — **Subtítulo:** "Conversations with EdTech founders about growth and impact."

---

Las 3 secciones (`#essencial`, `#investor`, `#founders`) ya tienen contenido completo — no quedan anchors vacíos.

### `.section` (sin modifier)
Las secciones ancla usan el `.section`/`.container` base del design system global, sin overrides todavía.
