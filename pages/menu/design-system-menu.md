# Site Menu Page — Sub Design System

Clases específicas de la página `/menu`. Complementan el design system global (`/design-system.md`).

Página de navegación simple que lista todas las páginas construidas del repo, incluida `/components` (kitchen sink de componentes). Reutiliza el mismo patrón visual que `/components` (lista vertical con bordes y hover invertido).

---

## Sección Site Menu

### `.section--site-menu`
Modifier de `.section`. Full-height (`min-height: 100vh`), centrado verticalmente.

### `.site-menu-container`
Modifier de `.container`. Gap de `--space-md` entre logo, eyebrow, título y lista.

### `.site-menu-logo`
Wrapper del logo (link a `/`). `img` a `2.5em` de alto.

### `.site-menu-list`
`nav` en columna, contiene los `.site-menu-item`.

### `.site-menu-item`
Cada link de la lista:
- `font-size: 1.75em` (desktop) / `21px` (mobile)
- `border-top: 1px solid var(--color-black)`; el último item también tiene `border-bottom`
- Hover: fondo negro, texto blanco, `padding-left` +0.5em

---

## Páginas listadas

| Página | Ruta |
|---|---|
| Home | `/` |
| Work | `/work` |
| Work CMS | `/work-cms` |
| The EdTech Mentor | `/edtech-mentor` |
| EdTech Mentor CMS | `/edtech-mentor-cms` |
| Resources | `/resources` |
| Resources CMS | `/resources-cms` |
| Clientes | `/clientes` |
| Components (Kitchen Sink) | `/components` |

> Cuando se cree una página nueva en el repo, agregar su link aquí y en `menu/index.html`.
