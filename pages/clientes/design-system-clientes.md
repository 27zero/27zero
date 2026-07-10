# Work Page — Sub Design System

Clases específicas de la página `/work`. Complementan el design system global (`/design-system.md`).

---

## Sección Hero

### `.section--hero`
Modifier de `.section`. Override de padding para el hero de la página Work.
- `padding-top: 18.21em` (255px @ 14px base)
- `padding-bottom: 5em` (70px @ 14px base)

### `.hero-container`
Modifier de `.container`. Ajusta el alineamiento horizontal del hero.
- `padding-left: 13em` — indentación específica del hero
- `gap: var(--space-xs)` — espaciado reducido entre eyebrow, H1 y subtext

---

## Sección Pills

### `.section--pills`
Modifier de `.section`. Anula el padding-top para que las pills queden pegadas al hero.
- `padding-top: 0`
- `padding-bottom: var(--space-sm)`

### `.pills-container`
Modifier de `.container`. Hereda el padding-left del hero para alineación visual.
- `padding-left: 13em`

### `.pills-wrap`
Contenedor flex con wrap para el grupo de filtros.
- `display: flex; flex-wrap: wrap; gap: 0.75em`

### `.pill`
Botón de filtro en estado inactivo. Outline negro, borde redondeado.
- Estado hover: borde y texto cambian a `--color-indigo`

### `.pill--active`
Modifier de `.pill`. Estado activo.
- Fondo y borde: `--color-purple`
- Texto: `--color-black`

---

## Sección Sliders

### `.section--sliders`
Modifier de `.section`. Sin padding-right para que el track de cards desborde hasta el borde de la pantalla.
- `padding-top: 0`
- `padding-bottom: var(--space-lg)`

### `.sliders-container`
Reemplaza al `.container` estándar en la sección de sliders. No tiene `max-width` ni `padding-right` para permitir que el track llegue al borde de la pantalla. El `padding-left` se hereda de la hoja de estilos directamente.

### `.slider-block`
Unidad completa de un slider: título + track + flechas.
- `display: flex; flex-direction: column`
- `gap: var(--space-md)` (70px @ 14px base)

### `.slider-header`
Contiene el título del slider. Tiene `padding-right` y `max-width` para que el título respete el contenedor mientras el track no.

### `.slider-title`
Título de cada categoría de slider.
- Inter, 500, `1.5em` (21px @ 14px), line-height 150%, letter-spacing 0

### `.slider-footer`
Contenedor de las flechas de navegación. Se ubica **debajo** del track, alineado a la derecha.
- `display: flex; justify-content: flex-end`

### `.slider-nav`
Wrapper flex para los dos botones de flecha.

### `.slider-arrow`
Botón circular de navegación del slider.
- Tamaño: `2.85em`
- Estado por defecto: fondo blanco, borde negro
- Estado hover (no disabled): fondo negro, ícono blanco
- Estado `disabled`: opacity 0.3, sin cambio en hover

**Lógica de estado:**
- `prev` → desactivado por defecto. Se activa cuando `scrollLeft > 2`
- `next` → activo por defecto si las cards desbordan el container. Se desactiva al llegar al final

### `.slider-track-wrap`
Wrapper del track. Sin `overflow: hidden` para que el corte lo haga el viewport.

### `.slider-track`
El track scrolleable horizontal.
- `overflow-x: auto`, scroll oculto, `cursor: grab`
- `padding-right: 6.5em` para que la última card no quede pegada al borde
- Clase `.dragging` (agregada por JS): cambia cursor a `grabbing` y desactiva `scroll-behavior: smooth`

---

## Cards

### `.card--work` (con `.card`)
Estructura base de las cards del slider. Posición relativa para superponer el `.card-work-bg` y el `.card-work-body`.

### `.card--featured`
Modifier de `.card`. Cards de la categoría "Los mejores".
- Ancho: `22em` — altura mínima: `26.5em`
- Forma rectangular vertical

### `.card--standard`
Modifier de `.card`. Cards de las demás categorías.
- Ancho: `18em` — altura mínima: `18em`
- Forma casi cuadrada 1:1

### `.card-work-bg`
Capa de fondo absoluta que simula la thumbnail del proyecto.
- Fondo: `--color-gray`
- Sin borde
- Contiene el texto placeholder `[PROJECT THUMBNAIL]`

### `.card-work-bg span`
Texto de wireframe dentro del fondo.
- `opacity: 0.4` — faded

### `.card-work-body`
Capa de contenido, z-index 1, encima del bg. Flex column con `justify-content: space-between`.

### `.card-work-content`
Agrupador vertical del contenido superior: eyebrow + title + client.
- `gap: 0.75em`

### `.card-work-footer`
Agrupador del contenido inferior: solo flecha de link.
- `justify-content: flex-end`

### `.card-work-eyebrow`
Etiqueta de categoría en la card.
- Inter, 400, `1.07em` (15px @ 14px), line-height 150%, letter-spacing 0

### `.card-work-title`
Titular del proyecto.
- Inter, 500, `1.71em` (24px @ 14px), line-height 140%, letter-spacing 0

### `.card-work-client`
Fila con logo circular + nombre del cliente. Va dentro de `.card-work-content`, debajo del título.

### `.card-work-client-logo`
Placeholder circular del logo del cliente.
- `1.71em` × `1.71em`, borde sutil, fondo blanco

### `.card-work-client-name`
Nombre del cliente en texto.
- Inter, 500, `1em`

### `.card-work-arrow`
Botón circular de link dentro de la card (esquina inferior derecha).
- `2.5em` × `2.5em`
- Hover de la `.card` completa activa el estado filled negro
