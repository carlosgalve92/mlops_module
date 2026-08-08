## Preparación Azure
Crear cuenta en Azure

- Crear cuenta de almacenamiento (Blob Storage)
- Crear contenedor dentro de la cuenta de almacenamiento.
- Crear VM Azure (Máquina Virtual de Azure)
    - **IMPORTANTE**: Guardar la clave privada (<nombre_clave>.pem) para luego poder acceder vía ssh. Esta clave se consigue cuando creas la maquina virtual, te aparece una ventana emergente preguntandote si quieres descargar la clave.
    - Se recomienda poner hora de apagado automática para evitar grandes costes.
- Dar acceso a la VM a la cuenta de almacenamiento
    - Habilitar en VM Azure Estado Identidad (Seguridad >> Identidad >> Asignado por el sistema)
    - Agregar asignación de Roles (Colaborador de datos de Storage Blob) en la cuenta de almacenamiento (Agregar asignación de roles)
- Se enciende la VM Azure

Configurar conexión ssh para que pueda ser utilizada por Visual Code
- Copiar fichero con clave privada (<nombre fichero>.pem) en ~/.ssh/
- Configurar fichero ~/.ssh/config pegando el texto de abajo con los datos de la máquina virtual de Azure

    ```
    Host azure-vm-python
        HostName <IP Publica>              # ← IP pública real de la VM
        User <usuario>                     # ← Nombre de usuario configurado al crear la VM
        IdentityFile <ruta fichero> # ← File con ruta donde se guarda la clave privada descargada
    ```

**IMPORTANTE:** Acordarse de apagar la VM Azure después de trabajar con ella.

## Preparación entorno Python con Poetry

En este proyecto se va a utilizar **Poetry** como gestor de paquetes y de entornos virtuales. Poetry se encarga de crear el entorno virtual, resolver las dependencias y dejarlas declaradas de forma reproducible en los ficheros `pyproject.toml` y `poetry.lock`.

El proyecto se va a crear en la ruta _~/projects/_ con nombre _mlops_module_.

### 1. Instalar dependencias del sistema

```
sudo apt-get update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv pipx -y
```

### 2. Instalar Poetry

La forma recomendada es mediante **pipx** (instala Poetry de forma aislada, sin contaminar el Python del sistema):

```
pipx install poetry
pipx ensurepath
```

Cierra y vuelve a abrir la terminal (o ejecuta `source ~/.bashrc`) y verifica la instalación:

```
poetry --version
```

> Alternativa con el instalador oficial:
> ```
> curl -sSL https://install.python-poetry.org | python3 -
> ```

### 3. Configurar Poetry

Se configura Poetry para que cree el entorno virtual **dentro de la propia carpeta del proyecto** (en `.venv`). Esto es útil para que Visual Studio Code lo detecte automáticamente y para tenerlo todo autocontenido:

```
poetry config virtualenvs.in-project true
```

### 4. Crear el proyecto con la estructura de paquete

Situándose en la carpeta `~/projects/`, se crea el proyecto con `poetry new`. Poetry genera automáticamente la carpeta y toda la estructura de un paquete Python (no hace falta `mkdir` previo):

```
mkdir -p ~/projects
cd ~/projects
poetry new --python ">=3.12,<4.0" mlops_module
```

Situarse en la carpeta mlops_module desde visual studio code

Esto crea la siguiente estructura:

```
mlops_module/
├── pyproject.toml          # configuración del proyecto y dependencias
├── README.md
├── src/
│   └── mlops_module/
│       └── __init__.py     # aquí va el código de tu paquete
└── tests/
    └── __init__.py         # aquí van los tests
```

El flag `--src` coloca el código dentro de una carpeta `src/` (disposición recomendada: obliga a instalar el paquete para usarlo, lo que evita errores de empaquetado ocultos). Si prefieres la disposición plana, omite el flag: `poetry new mlops_module`.

> Alternativa: si solo quieres generar el `pyproject.toml` sobre una carpeta ya existente (sin estructura de paquete), usa `poetry init`, que lanza un asistente interactivo.

### 5. Fijar la versión de Python (3.12)

```
poetry env use python3.12
```

Con esto se crea el entorno virtual en `.venv` usando Python 3.10.

### 6. Instalar y añadir librerías

Para instalar lo declarado en `pyproject.toml`:

```
poetry install
```

Para añadir nuevas librerías (Poetry las instala y actualiza `pyproject.toml` y `poetry.lock`):

```
poetry add pandas scikit-learn
```

Para dependencias que solo se usan en desarrollo (formateadores, linters, tests):

```
poetry add --group dev black ruff pytest
```

Para instalar lo declarado en `pyproject.toml` con el grupo dev:

```
poetry install --with dev
```

### 7. Activar el entorno y ejecutar código

Para ejecutar un comando puntual dentro del entorno virtual sin activarlo:

```
poetry run python -m mlops_module      # ejecuta el paquete (src/mlops_module)
poetry run pytest                      # ejecuta los tests de la carpeta tests/
```

Para activar el entorno virtual de forma interactiva:

```
eval $(poetry env activate)
```

> **Nota:** A partir de Poetry 2.0 el comando `poetry shell` dejó de venir por defecto. Si quieres recuperarlo puedes instalar el plugin:
> ```
> poetry self add poetry-plugin-shell
> poetry shell
> ```

## Control de versiones con Git

El código se va a versionar con **Git** y se va a alojar en **GitHub** como repositorio remoto.

### 1. Instalar y configurar Git

```
sudo apt install git -y
git config --global user.name "Tu Nombre"
git config --global user.email "tu_email@ejemplo.com"
git config --global init.defaultBranch main
```

### 2. Inicializar el repositorio

Situarse en la carpeta del proyecto e inicializar Git:

```
cd ~/projects/mlops_module
git init
```
