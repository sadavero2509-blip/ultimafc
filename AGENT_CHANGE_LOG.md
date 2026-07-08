# Bitácora de cambios del agente

Este archivo documenta los cambios importantes que el agente realice en el proyecto a partir de este momento.

Formato de entradas (una por cambio importante):

## YYYY-MM-DD
- **Motivo:** …
- **Qué hice (resumen):** …
- **Cómo lo hice (pasos):** …
- **Archivos tocados:** …
- **Comandos / scripts ejecutados:** …
- **Notas / riesgos / validación:** …

---

Entrada inicial:
- **Fecha:** 2026-05-26
- **Contexto:** Análisis inicial del proyecto para ubicar el flujo principal (`main.py`), el sistema de escenas (`scene_manager.py`), el cliente de red (`systems/network.py`) y el servidor (`server/app.py`).
- **Acción de trazabilidad:** Se creó este archivo (`AGENT_CHANGE_LOG.md`) para documentar cambios importantes desde este punto.

---

## 2026-05-26
- **Motivo:** Crear animaciones reales simplificadas para la “bolita”/elemento del jugador (movimiento + gestos), no solo un estado fijo.
- **Qué hice (resumen):** Actualicé `FieldPlayer.draw()` y `Goalkeeper.draw()` para introducir: respiración/bob, squash en tackle, sombra estirada, trail simple de movimiento, gesto de “brazos” durante pase/tíro (si tiene balón), blink facial, y anillo/chispas durante `goal_freeze` para el goleador. Además conecté `FieldPlayer.update()` con una referencia efímera al `match_scene` para que `draw()` pueda detectar `goal_freeze`.
- **Cómo lo hice (pasos):**
  1. Detecté que el render actual de jugadores es en círculos en `entities/field_player.py` (y portero en `entities/goalkeeper.py`), con lógica de pose/control en `update()`.
  2. Añadí variables de animación (`_anim_phase`, `_match_scene_ref`) y mantuve compatibilidad sin tocar física.
  3. En `FieldPlayer.update()` guardé `match_scene` cuando existe para que `draw()` sepa si está en `goal_freeze` (allí el `MatchScene` congela la lógica, pero `draw()` sigue).
  4. Reescribí el `draw()` de `FieldPlayer` para variar radio/y_offset/sombra y dibujar gestos (brazos, ojos y celebración).
  5. Aplicé una animación simplificada equivalente en `Goalkeeper.draw()` (bob, radio elástico, blink y subir guantes según carga).
  6. Ejecuté validación de lints para `field_player.py` y `goalkeeper.py`.
- **Archivos tocados:** `entities/field_player.py`, `entities/goalkeeper.py`
- **Comandos / scripts ejecutados:** `ReadLints` sobre los archivos modificados.
- **Notas / riesgos / validación:** Lints sin errores. La rotación de la franja se hace sólo cuando el ángulo supera ~1° (reduce trabajo). El modo celebración usa comparación por nombre del goleador contra `ms.ball.last_touch_name` durante `goal_freeze`. Si el nombre no coincide exactamente, la celebración puede no disparar en algunos casos.

---

## 2026-05-26
- **Motivo:** Permitir consultar el contrato en modos carrera (solo lectura) y añadir un mensaje de bienvenida con los detalles del contrato.
- **Qué hice (resumen):**
  - `CareerStatsScene`: mejoré la pestaña `CONTRATO` para mostrar duración restante y salario real (si `career_player["salary"]` existe; si no, fallback con `_calculate_salary`).
  - `CareerHubScene`: cuando el contrato aún tiene más de 2 años, el botón `CONTRATO` ahora abre la consulta del contrato (pestaña `contract`) en vez de bloquearte con un mensaje.
  - `career_manager.start_player_career()`: añadí un correo nuevo (`type="contract"`) con resumen del contrato (duración, rol y salario anual/semanal) a la bandeja de entrada.
- **Cómo lo hice (pasos):**
  1. Localicé dónde existe la pestaña `CONTRATO` (`scenes/career_stats.py`) y cómo se usa desde el hub (`scenes/career_hub.py`).
  2. Actualicé el tab `contract` para que use `contract_years` y `salary` del jugador (sin mezclarlo con valores de temporada).
  3. Añadí soporte en `CareerStatsScene` para abrir una pestaña concreta vía `context={"tab_id":"contract"}`.
  4. Cambié el comportamiento en `CareerHubScene` para abrir la consulta cuando la renovación no está habilitada.
  5. Añadí el nuevo email en `data/career_manager.py` al iniciar carrera de jugador.
- **Archivos tocados:** `scenes/career_stats.py`, `scenes/career_hub.py`, `data/career_manager.py`
- **Comandos / scripts ejecutados:** `py_compile` y `ReadLints` tras los cambios.
- **Notas / riesgos / validación:** El contenido del email se renderiza como texto (la bandeja no usa HTML). Hay un fallback para salary/role si faltan campos en `career_player`. El email se envuelve en líneas por la UI existente.
- **Ajuste posterior:** Eliminé `\n` del contenido del email para que el word-wrapping de `CareerInboxScene` lo muestre sin saltos/artefactos.
- **Ajuste posterior 2:** En `CareerStatsScene` cambié el fallback de `contract_years` de `0` a `3` para que la UI refleje el comportamiento esperado si faltara el dato.

---

## 2026-05-26
- **Motivo:** Añadir música y efectos de sonido de alta fidelidad (16-bit 44.1kHz) al juego.
- **Qué hice (resumen):** Escribí `generate_audio.py` para sintetizar audios naturales procedurales (PCM 16-bit 44.1kHz) usando FM y Pink Noise. Creé `systems/audio_manager.py` con `pygame.mixer` e integré reproducción de música de menú, sonidos de navegación, y sonidos de estadio (ambiente, pito, grito de gol).
- **Cómo lo hice (pasos):**
  1. Escribí un generador Python (`generate_audio.py`) que crea sonidos complejos sin depender de bibliotecas externas complejas.
  2. Implementé `systems/audio_manager.py` como Singleton para inicializar `pygame.mixer` y cargar los audios de forma segura.
  3. Integré la inicialización de audio en `main.py`.
  4. Intercepté las teclas en `scene_manager.py` para tener sonidos de navegación universales en la UI.
  5. Agregué música de fondo en `main_menu.py`.
  6. Agregué el ruido de estadio (`crowd_bg.wav`), el pitazo (`whistle.wav`) y el grito de gol (`goal_cheer.wav`) en los momentos clave de `match.py`.
- **Archivos tocados:** `generate_audio.py` (nuevo), `systems/audio_manager.py` (nuevo), `main.py`, `scene_manager.py`, `scenes/main_menu.py`, `scenes/match.py`
- **Comandos / scripts ejecutados:** `python generate_audio.py` para crear la carpeta y los archivos `.wav`.
- **Notas / riesgos / validación:** Los archivos .wav se generaron correctamente y la compilación no arrojó errores de sintaxis en `match.py` ni `main_menu.py`.

---

## 2026-05-26
- **Motivo:** Agregar múltiples géneros musicales para la música de fondo (Rock, Jazz, Ambiental, Electro) y rotación automática.
- **Qué hice (resumen):** Creado un generador de síntesis de música avanzada (`generate_music.py`) que crea pistas procedimentales de varios géneros usando Python puro a 16-bit 44.1kHz. Implementado un sistema de "playlist" en `AudioManager` que elige canciones al azar y avanza a la siguiente automáticamente cuando una pista termina (mediante evento `MUSIC_END_EVENT`).
- **Cómo lo hice (pasos):**
  1. Desarrollé el generador procedural con síntesis aditiva y AM/FM simple para crear timbres que imiten bajo walking, acordes de jazz, distorsión de guitarra y arpegios electrónicos.
  2. Modifiqué `systems/audio_manager.py` para cargar un playlist y gestionar `pygame.mixer.music.set_endevent`.
  3. Integré la captura del `MUSIC_END_EVENT` en el bucle principal (`main.py`) para llamar automáticamente a `play_next_song()`.
- **Archivos tocados:** `generate_music.py` (nuevo), `systems/audio_manager.py`, `main.py`
- **Comandos / scripts ejecutados:** `python generate_music.py`
- **Notas / riesgos / validación:** Comprobada la correcta integración de `MUSIC_END_EVENT` en el event loop principal del juego.

---

## 2026-06-03
- **Motivo:** Configurar cinemáticas de apertura de sobres diferenciadas basadas en la media del jugador (OVR), agregando sonido de walkout y partículas doradas a jugadores estrella (86+), sonido suave a paneles (83-85) y omitiendo la animación para comunes (82-).
- **Qué hice (resumen):**
  - Añadido soporte diferenciador en `scenes/ultimate_hub.py` para walkouts (OVR >= 86), paneles (OVR 83-85) y no paneles (OVR <= 82).
  - La cinemática de sobre solo se ejecuta para OVR >= 83. Las cartas de OVR <= 82 omiten la animación de sobre y muestran la cuadrícula de artículos directamente.
  - Para los caminantes estrella (OVR >= 86), se activa el efecto continuo de partículas doradas flotantes y se reproduce la pista dramática `walkout.wav`.
  - Para los paneles (OVR 83-85), se reproduce un sonido simple `select.wav` y no se dibujan las partículas doradas.
- **Cómo lo hice (pasos):**
  - Modificado el handler de apertura de sobres en `scenes/ultimate_hub.py` (para compras normales y sobres pendientes) para establecer la bandera `walkout_state = 1` sólo si OVR >= 83.
  - Editado `_draw_pack_reveal` en `scenes/ultimate_hub.py` para controlar la reproducción de audio al inicio y la generación y renderizado del bucle de partículas en base a si la media del jugador es >= 86.
- **Archivos tocados:** `scenes/ultimate_hub.py`
- **Comandos / scripts ejecutados:** compilación estática vía `python -m py_compile main.py scenes/ultimate_hub.py systems/audio_manager.py` (todos exitosos).
- **Notas / riesgos / validación:** La visualización de partículas doradas se protegió condicionalmente para evitar excepciones de atributo `_walkout_particles` cuando un panel (83-85) se renderiza en la cinemática.

---

## 2026-06-03 (Evoluciones UI/UX Redesign)
- **Motivo:** Rediseñar la interfaz y el flujo del Centro de Evoluciones para elegir primero la evolución y después el jugador compatible ordenado por media, incluyendo sugerencias visuales de mejora de cartas.
- **Qué hice (resumen):**
  - Cambiado el estado inicial a `EVO_SELECT`.
  - En `EVO_SELECT`, la interfaz muestra el catálogo a la izquierda, detalles de la evolución y una recomendación interactiva del mejor jugador compatible del club a la derecha (mostrando su carta original vs la carta mejorada simulada y sus incrementos de atributos).
  - Al presionar Enter sobre una evolución, si el club tiene jugadores elegibles, pasa al estado `PLAYER_SELECT` cargando la lista de jugadores compatibles ordenada de mayor a menor OVR.
  - En `PLAYER_SELECT`, se despliega una comparativa visual side-by-side de la carta original contra la carta evolucionada del jugador resaltado, detallando la suma de mejoras. Al presionar Enter se inicia la evolución y se cobran las monedas necesarias.
  - Añadido el control de retroceso rápido (tecla `ESCAPE`, `BACKSPACE`, `LEFT`) para salir de la selección de jugador.
- **Cómo lo hice (pasos):**
  - Implementado el helper `_get_evolved_preview` en `scenes/ultimate_hub.py` para calcular el incremento acumulado de estadísticas y recalcular el OVR simulado de la carta final de cualquier jugador.
  - Reescrita por completo la función `_draw_evolutions` con la nueva disposición de paneles adaptada para ambos estados (`EVO_SELECT` y `PLAYER_SELECT`).
  - Modificado el bloque de eventos de teclado de `EVOLUTIONS` en `handle_events` para manejar la redirección de flujo, validaciones de elegibilidad y monedas.
  - Modificado el handler universal de la tecla `ESCAPE` de la escena del Hub para capturar la transición hacia atrás de evoluciones.
- **Archivos tocados:** `scenes/ultimate_hub.py`
- **Comandos / scripts ejecutados:** `python -m py_compile main.py scenes/ultimate_hub.py` (exitoso).
- **Notas / riesgos / validación:** La simulación de mejora de estadísticas es dinámica, lo que permite previsualizar correctamente cualquier nivel sin modificar la base de datos real del club hasta la confirmación de la evolución.

---

## 2026-07-06
- **Motivo:** Corregir faltas muy estrictas, resolver el partido trabado tras expulsiones (tiros libres), habilitar ejecución del servidor en segundo plano sin terminal visible, corregir error de victorias registradas como derrotas por lado de cancha, y hacer que los pases al hueco vayan realmente al espacio libre.
- **Qué hice (resumen):**
  - **Faltas y Tarjetas:** Reduje la probabilidad base de falta al barrerse del 30% al 12% en `field_player.py`. Reduje amarillas, rojas y lesiones en `match.py`.
  - **Tiros Libres:** Agregué el estado `free_kick` para reanudar el partido desde donde ocurrió la falta.
  - **Congelación en Balón Parado:** Pausé el reloj del HUD y congelé a todos los jugadores e IA durante tiros libres, córners, saques de banda y de meta, reanudando la acción al instante de dar pase o tiro.
  - **Servidor Invisible:** Creé el script `iniciar_servidor_oculto.vbs` que ejecuta `iniciar_servidor.bat` en segundo plano ocultando la ventana de comandos.
  - **Corregir Determinación de Victoria:** Refactoricé `goal_celebration.py` para comparar el código corto del equipo (`user_team_short`) en vez de asumir que el usuario siempre está a la izquierda, corrigiendo el error que registraba derrotas tras el cambio de lado del entretiempo.
  - **Pase al Hueco Real:** Modifiqué la física y apuntado de `THROUGH` para enviar el balón a un punto adelantado (130-250px) en la dirección del movimiento/avance del receptor, mezclado con la dirección de apuntado analógica del usuario (35% de control de dirección). Evité que el receptor capture el balón instantáneamente por imán agregando una bandera `is_through_pass` en el balón que requiere que el cooldown de recepción expire antes de atraparlo.
- **Cómo lo hice (pasos):**
  1. Modifiqué `_check_foul_collision` en `entities/field_player.py` y `_handle_foul` en `scenes/match.py`.
  2. Implementé `free_kick` en `match.py` y modifiqué el bucle de actualización para detener el cronómetro y AI si `is_set_piece` es True.
  3. Modifiqué `entities/field_player.py` y `entities/goalkeeper.py` para forzar velocidad/actualización a 0 cuando hay set piece.
  4. Modifiqué `goal_celebration.py` para obtener `user_team_short` y comparar con `left_team.get("short")` para calcular goles a favor/en contra de manera dinámica.
  5. Editado `entities/ball.py` para agregar la bandera `is_through_pass`. Modificado `update()` y `_human_update` en `entities/field_player.py` para condicionar `can_capture` a la expiración de `receive_cooldown` si `is_through_pass` es True.
- **Archivos tocados:** `entities/field_player.py`, `entities/goalkeeper.py`, `entities/ball.py`, `scenes/match.py`, `scenes/goal_celebration.py`, `iniciar_servidor_oculto.vbs`, `parody_names.py`, `systems/card_renderer.py`
- **Comandos / scripts ejecutados:** `python -m py_compile scenes/goal_celebration.py scenes/match.py entities/field_player.py entities/goalkeeper.py entities/ball.py systems/card_renderer.py` (exitoso).

---

## 2026-07-06 (Parte 2)
- **Motivo:** Hacer que las cartas del Modo Ultimate muestren un único nombre (apellido/apodo principal) en lugar del formato "I. Apellido", y asegurar que todas las versiones de las cartas (Normal, World Cup, Flashback, Founder, Evo) reciban y muestren de forma idéntica este mismo nombre único.
- **Qué hice (resumen):**
  - Modifiqué `_format_player_name` en `systems/card_renderer.py` para extraer y retornar únicamente el apellido/nombre principal de la cadena completa.
  - Añadí una regla inteligente para detectar si el último término es un sufijo como `Jr.oh` (ej. `Vini Jr.oh`) en cuyo caso retorna el nombre completo correspondiente con el sufijo.
  - Como el gestor de Ultimate (`ultimate_manager.py`) ya normaliza internamente todos los nombres de cartas de eventos a su correspondiente nombre oficial en base de datos, con este formateador visual logramos que todas las versiones existentes y futuras (Normal, Mundial, Flashback, Evolución, etc.) muestren el mismo nombre único de forma 100% consistente.
- **Archivos tocados:** `systems/card_renderer.py`, `systems/updater.py`, `scenes/loading.py`, `server/app.py`, `settings.py`, `dist/NeoFutbolArcade_Release/installer.iss`
- **Comandos / scripts ejecutados:** `python -m py_compile systems/card_renderer.py systems/updater.py scenes/loading.py server/app.py settings.py` y recompilación en ejecutable con PyInstaller (exitoso).

---

## 2026-07-08
- **Motivo:** Implementar soporte completo de auto-actualización del ejecutable compilado (`.exe`), automatizar la sincronización de versiones (parche vs versión obligatoria) y resolver dinámicamente las rutas del ejecutable en el servidor.
- **Qué hice (resumen):**
  - **Auto-actualización del `.exe`**: Modifiqué `systems/updater.py` para detectar cuando corre congelado (`sys.frozen`), calcular el MD5 del exe en ejecución y descargarlo desde el servidor central si hay discrepancia. Al finalizar la descarga, escribe un script `.bat` temporal, sale limpiamente, y el script reemplaza el ejecutable en caliente y lo vuelve a lanzar.
  - **Visualización en Carga**: En `scenes/loading.py` añadí el soporte para mostrar el progreso de descarga de exe en porcentaje y lanzar el subproceso del bat al salir.
  - **Sincronización Automática de Parches**: Añadí `UPDATE_TYPE` en `settings.py` y modifiqué `server/app.py` para leer versión y tipo de actualización dinámicamente de `settings.py` (evitando valores hardcodeados).
  - **Búsqueda Dinámica de Exes**: En `/api/update/exe_info` y `/api/update/download_exe` implementé una función resolutora que escanea las rutas de distribución y desarrollo para encontrar el binario `NeoFutbolArcade.exe` más actualizado de forma secuencial y transparente.
- **Archivos tocados:** `systems/updater.py`, `scenes/loading.py`, `server/app.py`, `settings.py`, `dist/NeoFutbolArcade_Release/installer.iss`
- **Comandos / scripts ejecutados:** Recompilación del ejecutable `NeoFutbolArcade.exe` y del ZIP de distribución exitosamente.

