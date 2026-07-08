# Guía de Empaquetado para Android (APK) 📱

El proyecto ya cuenta con el archivo `buildozer.spec` configurado y los controles táctiles integrados en el código. Para generar el archivo APK, sigue estos pasos:

## Opción A: Usando Google Colab (Recomendado si usas Windows)
Como la compilación de Android requiere Linux, puedes usar este método gratuito:

1.  Crea un nuevo cuaderno en [Google Colab](https://colab.research.google.com/).
2.  Sube todos los archivos del proyecto al entorno de Colab.
3.  Ejecuta los siguientes comandos en una celda:

```bash
# 1. Instalar Buildozer y dependencias
!pip install --user --upgrade buildozer
!sudo apt update
!sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
!pip install --user Cython==0.29.33

# 2. Iniciar la compilación (Esto tardará entre 10-20 minutos)
!buildozer android debug
```

4.  Al finalizar, el APK estará en la carpeta `bin/` de Colab listo para descargar e instalar en tu móvil.

## Opción B: Usando Linux Local
Si tienes Linux (Ubuntu/Debian), simplemente corre:

```bash
buildozer android debug
```

## Notas Importantes
*   **Conexión al Servidor**: Asegúrate de que el archivo `server_config.json` tenga la **IP Pública** o la IP de tu red local donde esté corriendo el servidor Flask.
*   **Controles**: El juego detectará automáticamente que es Android y mostrará el joystick virtual y los botones A, B, X, Y.
*   **Modo Offline**: Si el móvil no tiene internet, el juego funcionará en modo offline guardando los datos locales hasta que se conecte.

¡Tu juego de fútbol ya es una realidad móvil! ⚽🔥
