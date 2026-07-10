# Marquee Logos — Sub Design System

Carrusel infinito de logos. Componente aislado en `/components/marquee-logos/`.

## Estructura

```
.marquee
  .marquee-list   (set 1 de logos)
  .marquee-list   (set 2, idéntico — aria-hidden="true")
```

Dos `.marquee-list` idénticas, en fila (flex). Ambas corren la misma animación (`marquee-scroll`, `0%` → `-100%`) en simultáneo: cuando la primera termina de salir por la izquierda, la segunda ya está ocupando exactamente su posición original — loop perfecto sin salto ni gap visual. La segunda lista lleva `aria-hidden="true"` porque es una copia puramente visual.

## Clases

- **`.marquee`** — wrapper, `overflow: hidden`, `display: flex`.
- **`.marquee-list`** — `gap: 3.21em` (45px), `flex-shrink: 0`, corre la animación.
- **`.marquee-logo`** — `max-height: 3.57em` (50px), `width: auto`, `object-fit: contain`.

## JS (`marquee-logos.js`)

La animación es 100% CSS (`@keyframes marquee-scroll`). El JS solo ajusta `animation-duration` según el ancho real del contenido (`scrollWidth`), para mantener una **velocidad constante en px/s** (default 60px/s) sin importar cuántos logos tenga cada lista — si no, agregar/quitar logos cambiaría la velocidad visual con una duración fija. Recalcula en `resize`. Soporta múltiples `.marquee` en la misma página.

## Assets

Logos en `/assets/logos/` (ya en kebab-case, nombres URL-safe): `doctums.svg`, `scholarship-magic.svg`, `skillwell.svg`, `student-first.svg`, `world-learning.svg`.

## Detalles

- Pausa en `:hover` (`.marquee:hover .marquee-list { animation-play-state: paused; }`).
- Respeta `prefers-reduced-motion: reduce` (desactiva la animación).
- Para que el loop se vea bien, cada `.marquee-list` debe tener suficiente contenido para llenar (o superar) el ancho del viewport — con pocos logos, considerar repetir el set de logos dentro de cada `.marquee-list` (no solo duplicar la lista completa).
