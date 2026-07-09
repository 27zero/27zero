# EdTech Mentor CMS — Design System

> Template de artículo individual (CMS) de la serie "The EdTech Mentor". Página de tipo blog article, con mucho contenido de texto. Analógica a `/work-cms` pero para un post de la serie de entrevistas.

---

## Estructura

1. **Navbar** — importado desde `/components/navbar` (html/css/js sin modificar).
2. **Hero** (`.section--hero-cms`) — breadcrumb, eyebrow de categoría, H1 (Lora), deck y meta row (autor, fecha, tiempo de lectura).
3. **Featured image** — placeholder de imagen destacada.
4. **Article body** (`.article-body`) — cuerpo de texto rico: párrafos, H2/H3/H4, blockquote con cita, lista, figura con caption.
5. **Author bio** — bloque de cierre con divider + bio del autor.
6. **Footer** — importado desde `/components/footer` (html/css sin modificar).

---

## Regla clave: H tags scoped

Esta página **no usa `h1`–`h4` como selector de tag global**. Todos los headings están scoped:

- `.section--hero-cms h1` → título del artículo (Lora, 2.9em desktop / 32px mobile).
- `.article-body h2` → secciones principales del artículo (2em desktop / 22px mobile).
- `.article-body h3` → subsecciones (1.5em desktop / 19px mobile).
- `.article-body h4` → headings menores dentro de una subsección (1.21em desktop / 16px mobile).

Motivo: al tratarse de una página con mucho texto (tipo blog), y siguiendo la advertencia del design system global (`/design-system.md`), un selector de tag suelto (`h2 { ... }`) pisaría los headings internos de componentes como `edtech-mentor-card`, `work-card` o `featured-card` si en el futuro se integran en esta página (sliders de "artículos relacionados", etc.). Escribir siempre el mismo selector scoped tanto en desktop como en el bloque `@media (max-width: 768px)` evita ese conflicto sin necesidad de `!important`.

---

## Tipografía en mobile — px fijos

Todos los tamaños de texto de esta página (headings scoped, `.text-body`, meta, blockquote, listas, figcaption, author bio) están definidos en `px` fijos dentro de `@media (max-width: 768px)`, nunca en `em`. El `em` en mobile queda reservado solo para espaciados (paddings, margins, gaps), tal como indica el design system global.

---

## Componentes importados

| Componente | Uso | Modificado |
|---|---|---|
| `/components/navbar` | Header fijo con variante `nav--white` | No — html/css/js intactos |
| `/components/footer` | Footer con columnas de links | No — html/css intactos |

---

## Tokens de color y espaciado

Reutiliza los tokens globales de `/design-system.md` (`--color-indigo`, `--color-purple`, `--color-black`, `--color-gray`, `--color-white`, `--space-xs` a `--space-2xl`), más un token propio de esta página:

```css
--article-width: 50em; /* ~700px — ancho de lectura del cuerpo del artículo */
```

---

## Placeholders de contenido

Todo el copy (título, deck, autor, cuerpo, cita, lista, bio) usa placeholders entre corchetes `[Así]`, siguiendo la misma convención que `/work-cms/index.html`, ya que este archivo es un template CMS reutilizable para cualquier entrada de la serie EdTech Mentor.
