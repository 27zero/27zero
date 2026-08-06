# Home Page — Sub Design System

Clases específicas de la página `/` (Home). Complementan el design system global (`/design-system.md`).

Este documento se va completando sección por sección a medida que se construye la página.

---

## Sección Hero

### `.section--hero-home`
Modifier de `.section`. Fondo `--color-gray`.
- `margin-top: 5.5em` (77px @ 14px) — espacio para el navbar fijo (ahora `nav--white` es transparent, así que este espacio ya no necesita ser "en blanco" estricto)
- `padding-top: 12.14em` (170px @ 14px)
- `padding-bottom: 12.14em` (170px @ 14px)
- Mobile (`≤768px`): `padding-top`/`padding-bottom: 18em`

### `.hero-home-container`
Modifier de `.container`.
- `align-items: flex-start`
- `gap: 1em`

### `.section--hero-home h1`
Override del H1 global, específico del hero de Home.
- Lora, weight 500, style normal, `3.43em` (48px @ 14px), line-height 125%, letter-spacing `-0.48px` (-1% de 48px)

### `.inter-accent` (dentro de `.section--hero-home h1`)
Span para la palabra de acento ("Brand power."), en Inter en vez de Lora, mismo tamaño/line-height/letter-spacing que el H1.
- Inter, weight 500, style normal, `1em` (hereda 48px del H1), line-height 125%, letter-spacing `-0.48px`

### `.hero-home-cta`
Wrapper del botón + caption. Los centra entre sí, independientemente del alineado del container.
- `display: flex; flex-direction: column; align-items: center; gap: 0.5em`
- `.hero-home-cta .btn-white` → `border-color: var(--color-white)` (override puntual solo en el hero)

### `.text-caption`
- Inter, weight 400, `1.07em` (15px @ 14px), line-height 160%, letter-spacing 0
- Mobile (`≤768px`): `font-size: 10px` (fijo, no em)

---

## Sección Intro

### `.section--intro-home`
Modifier de `.section`. Fondo `--color-purple`.
- `padding-top: 6.07em` (85px @ 14px)
- `padding-bottom: 6.07em` (85px @ 14px)

### `.intro-home-row`
Fila flex de dos columnas: texto a la izquierda, media a la derecha.
- `display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5em`
- Mobile (`≤768px`): `flex-direction: column`

### `.intro-home-text`
Columna de texto: H2 + párrafo + botón.
- `align-items: flex-start; gap: 1.5em` (21px @ 14px)
- `flex: 0 0 34%`

### `.section--intro-home h2`
Se eliminó el override — ahora hereda el H2 global sin estilos propios.

### `.intro-home-text h2:not(.slider-title)`
Override puntual del H2 dentro del bloque de texto (excluye `.slider-title` por si algún slider quedara anidado ahí).
- Lora, weight 500, style normal, `2.57em` (36px @ 14px), line-height 125%, letter-spacing `-0.36px` (-1% de 36px)

### `.inter-accent` (dentro de `.section--intro-home h2`)
Span para la frase de acento ("for growth and impact."). **Nota:** al quitar el override del H2 padre, este selector queda con valores fijos propios (Inter, 500, `1em`, line-height 125%, letter-spacing `-0.36px`) que ya no coinciden necesariamente con el tamaño del H2 global — revisar si aplica.

### `.intro-home-text p`
Reduce el párrafo del bloque intro a `1.07em` (15px @ 14px).

### `.intro-home-media`
Placeholder de imagen/video (equivalente a `.card-work-bg` pero como bloque suelto, no absoluto). Fondo `--color-gray`, texto centrado tipo wireframe con opacity 0.4.
- `flex: 1`
- `min-height: 34em`
- `border-radius: 0.5em`

### Slider "Los mejores" — componente `cards-slider` + `work-card`
**Importado directamente desde `/components/`, sin duplicar CSS/JS en esta página:**
- `<link>` a `/components/work-card/work-card.css` y `/components/cards-slider/cards-slider.css` en el `<head>`
- `<script>` a `/components/cards-slider/cards-slider.js` (antes de `/home/script.js`)
- Markup estático (no generado por JS) tal como está en `components/cards-slider/cards-slider.html`, 8 Work Cards placeholder, título "Los mejores"
- Envuelto en `.sliders-container` (única clase propia de Home, agrega `padding-top: 4.29em` (60px @ 14px) y `padding-bottom: 0` para separarlo del bloque intro — el resto de clases del slider/card vienen 100% del componente)
- `cards-slider.js` inicializa drag + flechas automáticamente sobre cualquier `.slider-block` presente en el DOM al cargar la página (por eso el markup debe ser estático, no inyectado por JS después)

---

## Sección "What sets 27zero apart" — componente `shapes-slider`

Implementado tal cual está en `/components/shapes-slider/` (HTML, CSS y JS sin modificar), como sibling entre la sección de "The EdTech Mentor" y la de Logos.

- **HTML:** markup copiado 1:1 de `components/shapes-slider/shapes-slider.html` (la parte del `<section>`, no el harness de preview standalone). Clase raíz `.shapes-slider` + las mismas clases del design system global que ya usa el resto de Home (`.section`, `.container`, `h2`, `h3`, `.text-body--sm`, `.btn`, `.btn-dark`) — no se agregó ni duplicó CSS nuevo en `home/style.css`.
- **CSS:** `<link>` a `/components/shapes-slider/shapes-slider.css` en el `<head>`. Todo el estilo específico del componente (`.apart-slider`, `.apart-slider-arrow`, `.apart-shapes-wrap`, `.apart-shapes`, `.apart-shape`, `.apart-shapes-nav-zone`, `.apart-shapes-spacer`, `.apart-home-scales`) va scoped bajo `.shapes-slider` dentro de ese archivo — nada de esto vive en `home/style.css`.
- **JS:** `<script>` a `/components/shapes-slider/shapes-slider.js` (antes de `/home/script.js`). Sin cambios: ya no es un slider que se mueve — es un bloque fijo de 3 shapes donde las flechas solo cambian el `scale` (activa 1, inactivas 0.9) y actualizan el título/texto de "Execution that Scales" (`#apartScalesTitle`/`#apartScalesText`) según la shape activa. En mobile se ocultan las flechas y se navega con swipe (scroll-snap) o tap en las zonas invisibles de los extremos (`.apart-shapes-nav-zone`).
- **Assets reutilizados:** `research-enhanced.png`, `execution.png`, `creativity.png` (ya existían en `/assets/`).

---

## Sección Logos

### `.section--logos-home`
Sección propia e independiente (ya no vive dentro de `.section--apart-home`).
- `padding-top: 0`
- `padding-bottom: 8.93em` (125px @ 14px)

### Marquee de logos — componente `marquee-logos`
**Importado directamente desde `/components/marquee-logos/`, sin duplicar CSS/JS:**
- `<link>` a `/components/marquee-logos/marquee-logos.css` en el `<head>`
- `<script>` a `/components/marquee-logos/marquee-logos.js` (auto-inicializa por `window.addEventListener('load', ...)` sobre cualquier `.marquee` del DOM — clona logos vía WAAPI hasta cubrir el viewport y anima loop infinito sin salto)
- Markup estático tal como está en `components/marquee-logos/marquee-logos.html`, con los 5 logos de `/assets/logos/`
- Sin clases propias de Home — todo el estilo viene del componente

---

## Sección "The EdTech Mentor"

Duplicado estructural del bloque de texto+media de Intro (`.section--intro-home`). **Ya no tiene slider** (se eliminó por completo: HTML, JS y CSS relacionados).

### `.section--mentor-home`
Fondo `--color-indigo`, `color: var(--color-white)` (cascada a H2, párrafo, etc.).
- `padding-top: 10.36em` (145px @ 14px)
- `padding-bottom: 5.71em` (80px @ 14px)

### `.mentor-home-row` / `.mentor-home-text`
Mismos estilos que `.intro-home-row` / `.intro-home-text` (duplicados 1:1, sin cambios de spacing).

### `.mentor-home-featured-wrap` — componente `featured-card`
Reemplaza el placeholder `.mentor-home-media` (ya no existe). Wrapper con `flex: 1; height: 30em`, conteniendo el componente real `featured-card` (`.card.card--featured`, `width/height: 100%`, se ajusta automáticamente al wrapper). **Nota:** se usa `height` (no `min-height`) porque el `height: 100%` del `.card--featured` necesita que el padre tenga una altura definida para resolver el porcentaje — con solo `min-height` la card no heredaba tamaño y quedaba chica. En mobile (`≤768px`) tanto el wrapper como `.card--featured` pasan a `height: auto` (el card ya no depende de una altura fija, se ajusta a su contenido) y `.card--featured` a `width: 100%`. `.card-featured-content` (del componente `featured-card`) también recibe `gap: 6.5em` en mobile. **Importado directamente desde `/components/`:**
- `<link>` a `/components/work-card/work-card.css` (ya estaba) y `/components/featured-card/featured-card.css` en el `<head>`
- Markup estático tal como está en `components/featured-card/featured-card.html`, contenido placeholder (Julie Kelleher / Kelleher Consulting Group)
- Sin JS propio

### `.section--mentor-home h2`
Mismo override que `.section--intro-home h2` (Lora 500, 2.57em, letter-spacing -0.36px).

### `.section--mentor-home .btn-white`
Botón usa la variante `.btn-white` (en vez de `.btn-dark` como en Intro), con `border-color: var(--color-white)` — mismo tratamiento que el botón del Hero, para que quede "full blanco" sobre el fondo indigo.

### Slider de `edtech-mentor-card` — sibling de `.mentor-home-container`
Componente `cards-slider` reutilizando el mismo `.sliders-container` de Intro (mismo padding, ya no se duplica CSS). **Sin título** — no se incluye `.slider-header`/`.slider-title`, el `.slider-block` va directo a `.slider-track-wrap`. Cards: 6 placeholders del componente `edtech-mentor-card` (`.card--edtech-mentor`, 25em, header transparente + body gray con gradiente/título en hover). **Importado directamente desde `/components/`:**
- `<link>` a `/components/edtech-mentor-card/edtech-mentor-card.css` en el `<head>` (además de `work-card.css` y `cards-slider.css`, ya presentes)
- Markup estático. `.section--mentor-home .slider-arrow` override scoped: borde/flecha blanca, bg transparente; hover invierte a bg blanco/flecha negra

---

## Sección Testimonials

### `.section--testimonials-home`
Fondo `--color-black`, `color: var(--color-white)`.
- `padding-top: 7.86em` (110px @ 14px)
- `padding-bottom: 4.64em` (65px @ 14px)

### `.testimonials-slider`
Carrusel de 1 slide por view (mismo mecanismo: flechas a los costados, track con `transform: translateX`, deshabilitado en los extremos — sin loop).
- `.testimonials-arrow`: clase propia (círculo, borde blanco, fondo transparente, hover invierte a blanco/negro) — independiente de `.slider-arrow` del componente `cards-slider` para evitar colisiones entre ambos
- `.testimonial-slide`: `justify-content: center` (slide centrado), quote SVG + `.testimonial-content` en fila
- `.testimonial-quote-icon`: el SVG del quote grande (path `#C286FF`), `width: 30em`
- `.testimonial-content`: `max-width: 30em`, `gap: 2.86em` (40px @ 14px)
- `.testimonial-text`: Inter 500, `1.5em` (21px @ 14px), line-height 150%, letter-spacing 0
- `.testimonial-divider`: línea blanca de 1px bajo el texto (ancho 100% del `.testimonial-content`, sin max-width propio)
- `.testimonial-author`: avatar circular placeholder (`.testimonial-avatar`, iniciales) + nombre/rol (`.testimonial-author-info`)
- `.testimonial-name`: Inter 400, `1.5em` (21px @ 14px)
- Mobile (`≤768px`): `.testimonial-slide` pasa a columna

### `.testimonials-dots`
Paginación por dots debajo del slider, sincronizada con el índice del carrusel (click en un dot navega directo a ese slide).
- `.testimonial-dot`: círculo outline blanco; `.testimonial-dot--active` → fondo/borde `--color-purple`

### Contenido
4 testimonios placeholder (`TESTIMONIALS` en `script.js`), el primero con el copy real dado ("Erin Grant"), el resto con Lorem ipsum — reemplazar cuando se tenga el contenido definitivo.

---

## Navbar y Footer

Integrados desde `/components/navbar/` y `/components/footer/`, tal como están definidos ahí (sin modificaciones):
- CSS: `<link>` a `/components/navbar/navbar.css` y `/components/footer/footer.css` en el `<head>`
- HTML: markup del `<header class="nav nav--white">` y del `<footer class="footer">` copiado tal cual del componente
- JS: `/components/navbar/navbar.js` (requiere `lottie-web` por CDN antes) para el estado `nav--scrolled` y el menú mobile animado
- El navbar es `position: fixed` (definido en su propio CSS). Variante usada: `nav--white`, consistente con el fondo claro del Hero
- El footer no requiere JS propio

## Work Card y Cards Slider

Integrados desde `/components/work-card/` y `/components/cards-slider/`, usados en el slider "Los mejores" (Intro, markup estático):
- CSS: `<link>` a `/components/work-card/work-card.css` y `/components/cards-slider/cards-slider.css` en el `<head>` (cargados después de `home/style.css`, junto con navbar/footer)
- JS: `/components/cards-slider/cards-slider.js` — auto-inicializa drag + flechas en cada `.slider-block` presente en el DOM al momento de cargar el script
- `home/style.css` ya **no** duplica `.slider-block`, `.slider-header`, `.slider-title`, `.slider-footer`, `.slider-nav`, `.slider-arrow`, `.slider-track-wrap`, `.slider-track`, `.card`, `.card-work-*` — todo viene del componente. Solo queda en `home/style.css` el override propio de la página: `.sliders-container` (spacing wrapper)
- **Nota histórica:** `.testimonials-arrow` (y `.apart-slider-arrow`, ya removido junto con toda la sección "What sets 27zero apart") reutilizaban antes la clase `.slider-arrow` para heredar su estilo — esto entraba en conflicto porque `.slider-arrow` ahora la define el componente `cards-slider.css`, cargado después en el `<head>`, pisando el estilo propio de esas secciones. Se desacoplaron dándoles su propio set de estilos completo (mismo look visual, sin depender de la clase del componente).

## Mobile (breakpoint estándar del proyecto: `max-width: 768px`)

Todos los media queries de `home/style.css` están unificados en **un único bloque `@media (max-width: 768px)` al final absoluto del archivo** (ya no hay reglas mobile intercaladas entre las de desktop). Esto es intencional: en un empate de especificidad, CSS resuelve por orden de aparición en el archivo, no por estar dentro de un media query — así que cualquier regla mobile que quedara antes de una regla base con la misma especificidad podía perder el empate y no aplicarse. Poniendo todo el mobile al final se garantiza que siempre gane **cuando la especificidad es igual**.

**Caso aparte — tipografía (`h1`-`h4`, `.text-body`, `.text-body--sm`, `.btn`):** primero se detectó un problema de **especificidad** (selectores de página con clase+elemento le ganaban a un simple `h1`/`h2`/`h3`), pero al forzar esas etiquetas globalmente con `!important` apareció un problema más de fondo: los tags `h2`/`h3` también los usan los componentes importados (`.slider-title` es un `h2`, y `.card-work-title`/`.card-featured-title`/`.card-edtech-mentor-title` son `h3`), así que el selector global les pisaba su propio tamaño. La solución: en vez de seleccionar el tag globalmente, el bloque mobile usa los **mismos selectores scoped que ya existían en desktop** (`.section--hero-home h1`, `.intro-home-text h2:not(.slider-title)`, `.section--mentor-home h2`) — así solo tocan el heading real de cada sección y nunca a los de las cards/slider. Al estar en el bloque mobile (al final del archivo), ganan por orden sobre su propia versión desktop sin necesitar `!important`. `h4` no se usa en ningún lado de Home, así que se quitó esa regla.

Cambios aplicados en `home/style.css`:

- **`.container`** (global, también documentado en `/design-system.md`): `padding-left`/`padding-right: 2em` en mobile, sin importar la página.
- **`.section--hero-home`**: `padding-top`/`padding-bottom: 12.86em` (180px @ 14px)
- **`.section--intro-home`**: `padding-top`/`padding-bottom: 6em` (84px @ 14px)
- **`.intro-home-row`**: `gap: 4.64em` (65px @ 14px)
- **`.intro-home-media`**: `width: 100%`
- **`.sliders-container`**: `padding-top: 3.93em` (55px @ 14px), `padding-left: 0`
- **`.section--mentor-home`**: `padding-top: 6.07em` (85px @ 14px), `padding-bottom: 4.5em` (63px @ 14px)
- **`.mentor-home-row`**: `gap: 4.64em` (65px @ 14px)
- **Testimonials**: `.testimonial-quote-icon` y `.testimonials-arrow` → `display: none`; `.testimonial-content` → `max-width: 100%` (el `max-width: 30em` de desktop lo achicaba innecesariamente, esto lo hace ocupar el ancho completo del container); `.testimonials-dots` → `gap: 1.2em`
