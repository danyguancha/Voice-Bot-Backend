
# Instalación de dependencias y rquisitos

Para asegurarte de que el sistema tenga todas las dependencias necesarias y que puedas usar el recurso de audio correctamente, sigue estos pasos:

1. **Instalación de dependencias**
Asegúrate de tener instaladas las siguientes dependencias en tu sistema:
ffmpeg (versión 2024-11-06)
Git (si aún no lo tienes instalado)
Si no tienes ffmpeg en tu sistema, sigue los pasos a continuación.

2. **Descargar el recurso de audio**
Visita el siguiente enlace para descargar la versión de ffmpeg que necesitas:
[ffmpeg 2024-11-06 builds](https://github.com/GyanD/codexffmpeg/releases/tag/2024-11-06-git-4047b887fc)

Descarga el archivo zip correspondiente a tu sistema operativo (Windows).

3. **Descomprimir el archivo**
Una vez descargado el archivo zip, descomprímelo en una ubicación de tu preferencia.

Ejemplo en Windows:

Crea una carpeta en C:\ffmpeg y descomprime el archivo zip dentro de ella.
4. Agregar la carpeta bin al PATH del sistema
Para asegurarte de que ffmpeg se pueda ejecutar desde cualquier lugar en la terminal, deberás agregar la carpeta bin (que contiene los ejecutables) al PATH de las variables de entorno de tu sistema.

## En Windows:
Navega a Panel de control → Sistema → Configuración avanzada del sistema.
Haz clic en Variables de entorno.
En la sección Variables del sistema, selecciona la variable Path y haz clic en Editar.
Haz clic en Nuevo y agrega la ruta completa de la carpeta bin que contiene los archivos de ffmpeg.
Ejemplo: C:\ffmpeg\bin.
Haz clic en Aceptar en todas las ventanas para guardar los cambios.

# Más dependencias
En el proyecto se ha creado un archivo **requirements.txt** l cual contiene las dependencias que se deben instalar en el entorno virtual. Para esto sigue los siguientes pasos.
1. **Creación del entorno virtual de python**
Ejecuta en consola el comando.
**python -m venv [nombre_del_entorno]**

2. **Activa el entorno virtual**
Ejecuta el comando:
**\.venv\Scripts\activate**

3. **Instala los requerimientos**
Ejecuta el comando:
**pip install -r requirements.txt**

Una vez instalado los requerimientos, podemos ejecutar el backend con e siguiente comando:

*uvicorn main:app --reload*


