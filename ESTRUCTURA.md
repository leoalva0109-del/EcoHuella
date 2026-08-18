# Estructura de carpetas de EcoHuella IA-Bio

Este proyecto es un sitio web estatico publicado con GitHub Pages. Por eso los
archivos HTML principales se quedan en la raiz del proyecto.

```text
EcoHuella/
|-- index.html
|-- fases.html
|-- ia.html
|-- tecnico.html
|-- materiales.html
|-- metodologia.html
|-- diagramas.html
|-- styles.css
|-- script.js
|-- serve-ecohuella.js
|-- assets/
|-- .github/
|-- .gitattributes
|-- .gitignore
|-- README.md
`-- ESTRUCTURA.md
```

## Raiz del proyecto

Aqui van los archivos que GitHub Pages necesita encontrar directamente.

- `index.html`: pagina principal.
- `fases.html`: separa Fase 1 ya validada y Fase 2 de integracion funcional.
- `ia.html`: modelo, metricas, capturas de entrenamiento y video del test de IA.
- `tecnico.html`: arquitectura, Jetson Nano, componentes y fuente LiFePO4.
- `materiales.html`: materiales, HDPE, panel solar principal y respaldo con bateria.
- `metodologia.html`: proceso de desarrollo del proyecto.
- `diagramas.html`: diagramas de bloques, flujo operativo y estados.
- `styles.css`: diseno visual, colores, tarjetas, responsive y fondos.
- `script.js`: menu movil, navegacion activa y zoom de diagramas.
- `serve-ecohuella.js`: servidor local para probar o compartir en red Wi-Fi.

## `assets/`

Carpeta para todos los archivos visuales y multimedia del sitio.

- Imagenes del prototipo y componentes.
- Capturas del entrenamiento de IA.
- Diagramas del sistema.
- Codigo QR de acceso rapido.
- Video del test del modelo de IA.

Conviene usar nombres simples, sin espacios ni acentos, por ejemplo:

```text
assets/test-modelo-ia.mp4
assets/qr-ecohuella.png
assets/paneles-solares-principal.png
```

## `.github/workflows/`

Carpeta de automatizacion de GitHub.

- `deploy.yml`: publica el sitio automaticamente en GitHub Pages cuando se suben cambios.

No necesitas modificar esta carpeta para cambiar contenido de la pagina.

## Archivos de configuracion

- `.gitignore`: evita subir archivos locales como `.vscode/` o `node_modules/`.
- `.gitattributes`: configura Git LFS para archivos grandes como videos `.mp4`.
- `README.md`: descripcion corta del proyecto y link publicado.

## Que editar segun lo que quieras cambiar

- Cambiar texto de inicio: `index.html`.
- Cambiar la division entre Fase 1 y Fase 2: `fases.html`.
- Cambiar metricas, entrenamiento o video: `ia.html`.
- Cambiar componentes electricos o Jetson: `tecnico.html`.
- Cambiar materiales o energia: `materiales.html`.
- Cambiar proceso de trabajo: `metodologia.html`.
- Cambiar diagramas: `diagramas.html`.
- Cambiar colores, tamanos o diseno: `styles.css`.
- Cambiar imagenes o video: reemplazar archivos dentro de `assets/`.

## Recomendacion

Manten los `.html` en la raiz. Si los mueves a otra carpeta, GitHub Pages puede
dejar de encontrar la pagina principal o habria que actualizar todos los enlaces.
