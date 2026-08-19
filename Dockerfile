# syntax=docker/dockerfile:1
# QUÉ HACE: le dice a Docker qué versión del parser de Dockerfile usar (el frontend BuildKit).
# POR QUÉ: sin esta línea, funciones como --mount=type=cache no están garantizadas.
#          La versión "1" es la estable y recibe mejoras sin romper nada, así que se deja fija.


# ---------------------------------------------------------------------------
# IMAGEN BASE
# ---------------------------------------------------------------------------
FROM python:3.12-slim
# QUÉ HACE: define la imagen base sobre la que se construye todo.
# POR QUÉ: python:3.12 ya trae Python instalado, y la variante "slim" elimina paquetes
#          del sistema que no necesitas, dando una imagen mucho más pequeña.
#          Menos tamaño = builds y despliegues más rápidos y menos superficie de ataque.


# ---------------------------------------------------------------------------
# VARIABLES DE ENTORNO (persisten en el contenedor)
# ---------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false
# PYTHONDONTWRITEBYTECODE=1
#   QUÉ HACE: evita que Python genere archivos .pyc.
#   POR QUÉ: en un contenedor efímero no aportan nada y solo ensucian la imagen.
# PYTHONUNBUFFERED=1
#   QUÉ HACE: desactiva el buffer de salida de Python.
#   POR QUÉ: hace que los logs aparezcan al instante; sin esto pueden quedar retenidos
#            y no verse hasta que el proceso termina.
# POETRY_VERSION=1.8.3
#   QUÉ HACE: fija la versión de Poetry.
#   POR QUÉ: sin fijarla, un build futuro podría instalar otra versión y comportarse
#            distinto. Builds reproducibles. (Cambia el número por la versión que uses.)
# POETRY_NO_INTERACTION=1
#   QUÉ HACE: evita que Poetry haga preguntas interactivas.
#   POR QUÉ: en un build automatizado no hay nadie para responder; una pregunta colgaría
#            el proceso.
# POETRY_VIRTUALENVS_CREATE=false
#   QUÉ HACE: hace que Poetry instale en el Python del sistema en vez de crear un venv.
#   POR QUÉ: el contenedor ya es un entorno aislado; un venv encima añade complejidad
#            y obligaría a activar rutas raras en el CMD.


# ---------------------------------------------------------------------------
# DEPENDENCIAS DE SISTEMA
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
# QUÉ HACE: instala git a nivel de sistema y borra la caché de apt.
#   apt-get update            -> refresca la lista de paquetes disponibles (obligatorio antes de instalar).
#   install -y git            -> instala git; el -y responde "sí" automáticamente.
#   --no-install-recommends   -> instala solo git, no los paquetes "recomendados" opcionales (ahorra espacio).
#   rm -rf /var/lib/apt/lists/* -> elimina los índices de apt descargados.
# POR QUÉ git: pip/Poetry lo necesitan si alguna dependencia se instala desde un repositorio.
# POR QUÉ el rm en la MISMA línea: cada RUN crea una capa; si borraras la caché en un RUN
#          aparte, la capa anterior seguiría cargando con ella. Uniéndolo, la capa queda ya limpia.


# ---------------------------------------------------------------------------
# INSTALACIÓN DE POETRY
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==$POETRY_VERSION"
# QUÉ HACE: instala la herramienta Poetry en sí, usando la caché de pip.
#   --mount=type=cache,target=/root/.cache/pip -> monta un directorio de caché que persiste
#                                                 ENTRE builds.
# POR QUÉ: si reconstruyes la imagen, pip reutiliza los paquetes ya descargados en lugar de
#          bajarlos otra vez. Acelera mucho los builds repetidos.


# ---------------------------------------------------------------------------
# DIRECTORIO DE TRABAJO
# ---------------------------------------------------------------------------
WORKDIR /mlops_module
# QUÉ HACE: fija el directorio de trabajo dentro del contenedor y lo crea si no existe.
# POR QUÉ: a partir de aquí todos los comandos (COPY, RUN, CMD) se ejecutan desde /webinar.
#          Evita rutas absolutas y mantiene el código ordenado en un sitio.


# ---------------------------------------------------------------------------
# DEPENDENCIAS DEL PROYECTO (primero, para aprovechar la caché de capas)
# ---------------------------------------------------------------------------
COPY pyproject.toml poetry.lock ./
# QUÉ HACE: copia SOLO los dos archivos que definen las dependencias.
# POR QUÉ (lo más importante del archivo): Docker construye por capas y cachea cada una.
#          Si copiaras todo el código antes de instalar, cualquier cambio en cualquier archivo
#          invalidaría la caché y reinstalaría TODAS las dependencias. Copiando primero solo
#          estos dos, la instalación pesada solo se repite cuando cambian de verdad las dependencias.

RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-root --only main
# QUÉ HACE: instala las dependencias del proyecto.
#   --no-root  -> instala las dependencias pero NO tu propio paquete.
#                 POR QUÉ: tu código aún no está copiado; instalar el paquete ahora fallaría.
#                 Además separa la capa "dependencias" (pesada, estable) de la de "tu código"
#                 (ligera, cambia mucho).
#   --only main -> instala solo el grupo principal, sin dependencias de desarrollo (pytest, linters...).
#                 POR QUÉ: en producción no las necesitas y solo engordan la imagen.
#                 (Si no separas grupos en pyproject.toml, quita el --only main aquí y abajo.)


# ---------------------------------------------------------------------------
# CÓDIGO FUENTE
# ---------------------------------------------------------------------------
COPY . .
# QUÉ HACE: copia todo el código fuente del proyecto al contenedor.
# POR QUÉ va aquí y no antes: al colocarlo DESPUÉS de instalar dependencias, un cambio en tu
#          código no invalida la capa de dependencias. Cambias código -> rebuild rápido;
#          cambias dependencias -> rebuild completo.

RUN poetry install --only main
# QUÉ HACE: ahora sí instala TU paquete (sin volver a bajar dependencias, que ya están).
# POR QUÉ: registra tu proyecto en el entorno para que sea importable/ejecutable.
#          Es rápido porque el trabajo pesado ya se hizo antes.


# ---------------------------------------------------------------------------
# USUARIO SIN PRIVILEGIOS (seguridad)
# ---------------------------------------------------------------------------
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /mlops_module
USER appuser
# QUÉ HACEN: crean un usuario normal con su carpeta home y cambian a él para el resto del
#            build y la ejecución.
# POR QUÉ: por defecto los contenedores corren como root; si comprometen la app tendrían
#          privilegios totales. Ejecutar como usuario sin privilegios limita el daño posible.
#          Es una práctica estándar de seguridad.


# ---------------------------------------------------------------------------
# PUERTO
# ---------------------------------------------------------------------------
EXPOSE 8000
# QUÉ HACE: documenta que la aplicación escucha en el puerto 8000.
# POR QUÉ (con matiz): NO abre ni publica el puerto por sí solo; es informativo y sirve a
#          herramientas y a otras personas para saber qué puerto usa. La publicación real se
#          hace al ejecutar con: docker run -p 8000:8000


# ---------------------------------------------------------------------------
# COMANDO DE ARRANQUE
# ---------------------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# QUÉ HACE: define el comando por defecto que se ejecuta al arrancar el contenedor.
#   uvicorn        -> el servidor ASGI que sirve FastAPI.
#   main:app       -> busca el objeto "app" dentro del módulo main.py.
#   --host 0.0.0.0 -> escucha en todas las interfaces.
#                     POR QUÉ es clave: con 127.0.0.1 la app solo sería accesible DENTRO del
#                     contenedor y no podrías conectarte desde fuera.
#   --port 8000    -> puerto donde escucha, coincide con el EXPOSE.
# POR QUÉ CMD y no RUN: RUN se ejecuta al CONSTRUIR la imagen; CMD se ejecuta al ARRANCAR el
#          contenedor. Y en formato de lista ["...", "..."] para que el proceso reciba las
#          señales del sistema correctamente (importante para que el contenedor se pare bien).
