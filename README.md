# ⚡ OmniVR Player 8K — Reproductor de Video VR por GPU
### *Inspirado en GoPro VR Player 3.0.5 con Aceleración por Hardware NVIDIA RTX*

**OmniVR Player 8K** es un reproductor de video de realidad virtual de alto rendimiento para Windows, diseñado para reproducir contenido **8K a 60/120 FPS** sin caídas de cuadros mediante decodificación directa por GPU (**NVIDIA NVDEC / Direct3D 11 Video Acceleration**).

---

## 🚀 Características Principales

### 1. 🎬 Decodificación 8K por GPU
- Compatible con **HEVC/H.265, AV1, VP9, H.264, ProRes, CineForm**.
- Tubería de renderizado sin copias intermedias a CPU: la decodificación ocurre directamente en los chips NVDEC de la **NVIDIA RTX 5090**, enviando los fotogramas a una textura FBO OpenGL en VRAM.
- Modos de calidad seleccionables:
  - **8K Nativo**: FBO completo (7680×3840 / 7680×4320) para máxima nitidez.
  - **4K Ultra**: Optimizado para 120 FPS sostenidos.
  - **Adaptativo**: Ajustado dinámicamente a la resolución de tu monitor.

### 2. 🪐 Modos de Proyección (Estilo GoPro VR Player)
1. **Rectilíneo (Normal)**: Perspectiva de cámara tradicional con campo visual ajustable (FOV 30° - 130°).
2. **Little Planet (Pequeño Planeta)**: La clásica proyección estereográfica hacia el nadir (suelo) característica de GoPro VR Player / Kolor Eyes, transformando el entorno en un planeta esférico miniatura.
3. **Ojo de Pez (Fisheye)**: Proyección circular equidistante y ultra-angular (hasta 200°).
4. **Panini (Vedutismo)**: Proyección cilíndrica que conserva las líneas verticales rectas incluso con ángulos de visión horizontales extremos (110° - 160°).
5. **Esférico 360°**: Mapa panorámico equirrectangular completo interactivo.

### 3. 🕶️ Formatos Estereoscópicos 3D & VR 180°
- **VR 180 Side-by-Side (SBS)**:
  - Ojo Izquierdo (mono 180°)
  - Ojo Derecho (mono 180°)
  - Dual Estéreo (pantalla dividida para visores VR / Meta Quest / gafas 3D)
  - Anaglifo 3D (Rojo / Cian para gafas 3D tradicionales)
- **360° Side-by-Side (SBS)**: Ojo Izq, Ojo Der, Dual Estéreo, Anaglifo 3D.
- **360° Over-Under (Arriba-Abajo / Top-Bottom)**: Ojo Superior, Inferior, Dual, Anaglifo 3D.
- **2D Mono 360°**: Visualización equirrectangular estándar.

### 4. 🖱️ Controles de Cámara e Interacción
- **Arrastre con Botón Izquierdo**: Rotación suave de Yaw (paneo horizontal) y Pitch (inclinación vertical) con inercia y amortiguación física.
- **Arrastre con Botón Derecho**: Rotación de Roll (inclinación de horizonte / peralte).
- **Rueda del Ratón**: Zoom / ajuste de campo visual (FOV) continuo y fluido.
- **Auto-Giro (Auto-Orbit)**: Rotación panorámica cinemática continua.
- **Centrado Instantáneo (R)**: Animación suave para volver al horizonte y orientación frontal (0°, 0°, 0°).
- **Auto-Detección Inteligente por Nombre de Archivo**: Reconoce automáticamente modos estéreo, cobertura de domo (180° / 190°) y modelos de lente ópticos a partir de patrones en el archivo (`8K_FISHEYE190`, `180x180_3dh`, `8K_LR_180`, `canon`, `rf5.2`, `tb`, `ou`). Totalmente personalizable desde *Herramientas → Configurar Detección por Nombre de Archivo...*.

### 5. 🎛️ Interfaz de Usuario Estudio Dark
- Barra superior e inferior translúcidas con efecto cristal (glassmorphism) que se **ocultan automáticamente** a los 3.5 segundos de inactividad del ratón.
- Barra de línea de tiempo con tiempo transcurrido / total (`00:00 / 00:00`) y búsqueda precisa.
- Control de volumen, velocidad de reproducción (0.25x a 2.0x), botón de bucle (loop) e inversión horizontal/vertical (Flip X / Flip Y).
- **HUD de Diagnóstico en Tiempo Real**: Muestra el estado del decodificador por hardware (`NVDEC`), resolución, FPS reales, pérdida de cuadros y ángulos exactos de la cámara.
- **Diálogos Glassmorphic de Alto Contraste**: Ventanas de atajos, información técnica y administrador de patrones con estética oscura y tipografía nítida.

---

## ⌨️ Atajos de Teclado

| Tecla | Acción |
| :--- | :--- |
| `Espacio` | Reproducir / Pausar |
| `P` | Rotar cíclicamente la proyección (Rectilíneo → Planet → Fisheye → Panini → 360°) |
| `1` - `5` | Proyecciones directas (1: Rectilíneo, 2: Planet, 3: Fisheye, 4: Panini, 5: 360°) |
| `+` / `=` | Acercar Zoom (Disminuir ángulo FOV) |
| `-` / `_` | Alejar Zoom (Aumentar ángulo FOV) |
| `0` | Restablecer FOV a 90° estándar |
| `R` | Centrar vista / Resetear cámara a 0° |
| `I` | Alternar inversión de ambos ejes de navegación (Inverted Axes) |
| `H` | Mostrar / Ocultar HUD de telemetría e información técnica |
| `F` o `F11` | Alternar Pantalla Completa |
| `←` / `→` | Retroceder / Avanzar 5 segundos |
| `Shift` + `←` / `→` | Retroceder / Avanzar 10 segundos |
| `↑` / `↓` | Subir / Bajar volumen (+/- 5%) |
| `M` | Silenciar / Activar audio (Mute) |
| `Ctrl + O` | Abrir cuadro de diálogo de archivo |
| `Doble Clic` | Alternar Pantalla Completa |
| `Clic Derecho` | Abrir Menú Contextual In-Viewport (100% visible en pantalla completa) |
| `Arrastrar y Soltar` | Suelta cualquier archivo `.mp4`, `.mkv`, `.mov`, `.360` en la ventana |

---

## 📁 Archivos Incluidos

- [main.py](file:///c:/tests/VRplayer/main.py): Punto de entrada de la aplicación.
- [ui_main_window.py](file:///c:/tests/VRplayer/ui_main_window.py): Interfaz gráfica moderna en PySide6.
- [vr_engine.py](file:///c:/tests/VRplayer/vr_engine.py): Motor OpenGL, manejo de FBOs 8K y cámara interactiva.
- [vr_shader.py](file:///c:/tests/VRplayer/vr_shader.py): Shaders GLSL para todas las proyecciones y modos estereoscópicos.
- [player_backend.py](file:///c:/tests/VRplayer/player_backend.py): Backend de libmpv configurado para aceleración GPU NVDEC.
- [run_player.bat](file:///c:/tests/VRplayer/run_player.bat): Acceso directo para ejecutar el reproductor o arrastrar videos encima.
- [generate_test_media.py](file:///c:/tests/VRplayer/generate_test_media.py): Generador de patrones de prueba 8K 360 y VR180 SBS.
- **Videos de prueba ya generados**:
  - `test_vr360_8k.mp4`: Video de prueba 8K (7680x3840 @ 60 FPS) con cuadrícula equirrectangular, coordenadas y puntos cardinales.
  - `test_vr180_sbs.mp4`: Video de prueba VR180 Side-by-Side estereoscópico (3840x1920 @ 60 FPS).

---

## 🛠️ Requisitos e Instalación

### 1. Requisitos Previos
* **Python**: 3.10 o superior (64-bit recomendado).
* **GPU**: Tarjeta gráfica compatible con OpenGL 3.3+ (NVIDIA GeForce RTX recomendada para aceleración por hardware NVDEC 8K).
* **libmpv (Windows)**:
  OmniVR Player utiliza `libmpv` a través de `python-mpv`. Requiere que `mpv-2.dll` o `libmpv-2.dll` esté presente en la raíz del proyecto o en el PATH del sistema.
  > **Nota**: Puedes obtener la compilación oficial de libmpv para Windows desde los [releases de mpv-player (shinchiro / mpv-builds)](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/) o mediante gestores de paquetes como Scoop (`scoop install mpv`).

### 2. Instalación de Dependencias
Clona el repositorio e instala los paquetes necesarios:

```powershell
git clone https://github.com/tu-usuario/OmniVR-Player-8K.git
cd OmniVR-Player-8K
pip install -r requirements.txt
```

---

## 🏃 Cómo Iniciar

Puedes iniciar el reproductor de dos formas:

1. **Haciendo doble clic** en `run_player.bat` (o arrastrando cualquier archivo de video sobre él).
2. **Desde la terminal**:
   ```powershell
   python main.py
   # o pasando un video directamente:
   python main.py "ruta\al\video_8k.mp4"
   ```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.

