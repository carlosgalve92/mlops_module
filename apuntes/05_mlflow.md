# MLflow

**MLflow** es una plataforma de código abierto para gestionar el ciclo de vida completo de los proyectos de *Machine Learning*: el seguimiento de experimentos, el empaquetado de código reproducible, la gestión de modelos y su despliegue. Es agnóstica respecto a la librería de ML (funciona con scikit-learn, PyTorch, TensorFlow, etc.) y al entorno de ejecución.

## Componentes principales

MLflow se organiza en cuatro componentes complementarios que cubren distintas fases del ciclo de vida de un proyecto de ML. Pueden usarse de forma independiente o combinada.

### MLflow Tracking

Es el componente central y el que interactúa con el almacenamiento. Registra y permite consultar los **experimentos**, entendidos como agrupaciones de ejecuciones (*runs*). De cada *run* almacena:

- **Parámetros** (*params*) — valores de entrada de la ejecución (hiperparámetros, configuración): tasa de aprendizaje, número de estimadores, etc.
- **Métricas** (*metrics*) — valores numéricos de salida que miden el rendimiento (*accuracy*, *loss*, *F1*). Pueden registrarse en distintos pasos, lo que permite graficar su evolución.
- **Artefactos** (*artifacts*) — ficheros de salida: modelos serializados, gráficas, matrices de confusión, datasets, etc.
- **Tags y metadatos** — información adicional como la versión del código (*commit* de Git), el autor o el momento de ejecución.

Ofrece una **interfaz web (UI)** para comparar ejecuciones, ordenarlas por métricas y visualizar la evolución de los experimentos. La interacción se realiza mediante la API de Python (`mlflow.log_param`, `mlflow.log_metric`, `mlflow.log_artifact`), aunque también dispone de API REST y CLI.

### MLflow Projects

Define un **formato estándar para empaquetar código** de ciencia de datos de forma reproducible. Un proyecto es un directorio (o repositorio Git) que incluye un fichero de configuración `MLproject`, donde se declaran:

- El **entorno** de ejecución (Conda, un contenedor Docker o el sistema local) con sus dependencias.
- Los **puntos de entrada** (*entry points*): los comandos ejecutables y sus parámetros.

Su objetivo es que cualquier persona pueda reejecutar el mismo experimento, con las mismas dependencias, mediante `mlflow run`, garantizando la reproducibilidad.

### MLflow Models

Establece un **formato estándar para empaquetar modelos** entrenados, de modo que puedan servirse en distintos entornos sin reescribir código. La pieza clave es el concepto de ***flavors*** (sabores): un mismo modelo se guarda con uno o varios formatos que definen cómo cargarlo y usarlo (por ejemplo, el *flavor* `python_function` genérico, o *flavors* específicos como `sklearn`, `pytorch` o `tensorflow`).

Gracias a este formato común, un modelo puede desplegarse de múltiples maneras: como **API REST** (`mlflow models serve`), en procesamiento por lotes (*batch*), en Spark o empaquetado en un contenedor Docker.

### MLflow Model Registry

Es un **repositorio centralizado** para gestionar el ciclo de vida de los modelos una vez entrenados. Sobre un modelo registrado permite:

- **Versionado** — cada vez que se registra un modelo con el mismo nombre se crea una nueva versión, conservando el historial.
- **Etapas** (*stages*) — transicionar cada versión entre fases: *None*, *Staging*, *Production* y *Archived*, reflejando su estado en el flujo de trabajo.
- **Anotaciones y trazabilidad** — describir versiones, registrar quién promovió un modelo a producción y cuándo, y enlazar cada versión con el *run* que la generó.

Actúa como puente entre el entrenamiento y el despliegue, aportando gobernanza sobre qué modelo está en producción en cada momento.

---

## Arquitectura de almacenamiento en MLflow Tracking

Para entender **dónde se almacenan los artefactos** es imprescindible conocer que MLflow Tracking separa el almacenamiento en **dos áreas distintas**, con propósitos diferentes:

- **Backend Store** — guarda los **metadatos** de los experimentos: parámetros, métricas, *tags* y la información de cada *run*. Son datos estructurados y ligeros. Puede ser un sistema de ficheros local o una base de datos SQL (PostgreSQL, MySQL, SQLite).
- **Artifact Store** — guarda los **artefactos**: los ficheros de salida, normalmente **pesados**, que produce cada ejecución (modelos serializados, gráficas, imágenes, datasets, ficheros de entorno, etc.).

Esta separación es deliberada: los metadatos son pequeños y se consultan constantemente (encajan en una base de datos), mientras que los artefactos son grandes y se almacenan mejor en un sistema pensado para objetos voluminosos, como un *object storage* en la nube.

### El Artifact Store

El **Artifact Store** es el lugar donde MLflow deposita los artefactos. Por defecto, MLflow los guarda en un directorio local `./mlruns`, pero para volúmenes de datos grandes admite ubicaciones remotas: Amazon S3, **Azure Blob Storage**, Google Cloud Storage, SFTP y NFS, entre otras.

Un detalle importante de arquitectura: las credenciales de acceso al *artifact store* se configuran **una sola vez durante la inicialización del servidor de *tracking***, de modo que los usuarios no tengan que gestionar credenciales en cada operación con artefactos.

---

## Almacenamiento de artefactos en Azure Blob Storage

Azure Blob Storage es un servicio de *object storage* idóneo como *artifact store*, ya que ofrece alta durabilidad y disponibilidad para ficheros voluminosos.

### El URI de Azure Blob Storage

Para indicar a MLflow que almacene los artefactos en Azure Blob Storage se especifica un URI con el esquema `wasbs://` o , con `abfss://` la siguiente forma:

```
abfss://<contenedor>@<cuenta_almacenamiento>.blob.core.windows.net/
```

Donde:

- `<contenedor>` — el contenedor de blobs dentro de la cuenta de almacenamiento.
- `<cuenta_almacenamiento>` — el nombre de la cuenta de almacenamiento de Azure.

### Dependencia necesaria

Para que MLflow pueda comunicarse con Azure Blob Storage es necesario instalar el paquete correspondiente, **tanto en el cliente como en el servidor de *tracking***:

```bash
pip install azure-storage-blob
pip azure-storage-file-datalake
```

### Autenticación

MLflow espera que las credenciales de acceso a Azure Storage estén disponibles a través de **variables de entorno**, o bien mediante la clase `DefaultAzureCredential()` del SDK de Azure. Las opciones principales son:

- **`AZURE_STORAGE_CONNECTION_STRING`** — la cadena de conexión completa de la cuenta de almacenamiento (tiene prioridad si está definida).
- **`AZURE_STORAGE_ACCESS_KEY`** — la clave de acceso de la cuenta de almacenamiento.
- **`DefaultAzureCredential()`** — cadena de autenticación del SDK de Azure que prueba automáticamente varios métodos (identidad administrada, variables de entorno, sesión de Azure CLI, etc.).

> **Importante:** la credencial elegida debe configurarse **en ambos lados**: en la aplicación cliente y en el servidor de *tracking* de MLflow.

Ejemplo con cadena de conexión:

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=<cuenta>;AccountKey=<clave>;EndpointSuffix=core.windows.net"
```

Ejemplo con clave de acceso:

```bash
export AZURE_STORAGE_ACCESS_KEY="<clave_de_acceso>"
```

### Autenticación mediante identidad administrada (recomendada en Azure)

Cuando MLflow se ejecuta sobre una máquina virtual de Azure con una **identidad administrada** y un **rol RBAC** sobre la cuenta de almacenamiento, se puede prescindir de claves y cadenas de conexión: `DefaultAzureCredential()` detecta y utiliza la identidad de la VM automáticamente.

Para ello, el rol asignado debe ser de **plano de datos** —típicamente **`Storage Blob Data Contributor`**— y no `Contributor` a secas, ya que este último gestiona la cuenta pero no concede acceso a los blobs. Es un error frecuente asignar `Contributor` y obtener un fallo de autorización al escribir artefactos.

---

## Arranque del servidor de tracking con Azure Blob Storage

El servidor de *tracking* se lanza indicando el *backend store* (para los metadatos) y el destino de artefactos (para el *artifact store* en Azure):

```bash
pip install azure-storage-blob

mlflow server \
  --backend-store-uri <url_base_de_datos> \
  --artifacts-destination wasbs://<contenedor>@<cuenta_almacenamiento>.blob.core.windows.net \
  --host 0.0.0.0 \
  --port 5000
```

- `--backend-store-uri` — ubicación de los metadatos (p. ej. una base de datos PostgreSQL).
- `--artifacts-destination` — ubicación de los artefactos en Azure Blob Storage.
- `--host 0.0.0.0` — hace que el servidor escuche en todas las interfaces (necesario para que sea accesible desde fuera de la propia máquina).

---

## Ejemplo de registro de artefactos desde el cliente

Una vez configurado el servidor y las credenciales, el código de entrenamiento apunta al servidor de *tracking* y registra parámetros, métricas y artefactos con normalidad. MLflow se encarga de depositar los artefactos en Azure Blob Storage de forma transparente:

```python
import mlflow

# Apuntar al servidor de tracking
mlflow.set_tracking_uri("http://<host_servidor>:5000")
mlflow.set_experiment("mi_experimento")

with mlflow.start_run():
    # Registrar parámetros y métricas (van al backend store)
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", 0.94)

    # Registrar un artefacto (va al artifact store: Azure Blob Storage)
    mlflow.log_artifact("matriz_confusion.png")

    # Registrar un modelo (también como artefacto)
    mlflow.sklearn.log_model(modelo, "modelo")
```

En este flujo, los parámetros y las métricas se almacenan en el *backend store*, mientras que la imagen y el modelo se suben al contenedor de Azure Blob Storage configurado como *artifact store*.

> **Nota sobre la visualización en la UI:** en algunas configuraciones, los artefactos almacenados en Azure Blob Storage **no se previsualizan directamente en la interfaz web de MLflow**. En esos casos es necesario descargarlos mediante un cliente de *blobs* (el portal de Azure, `az storage blob download`, el SDK de Azure o la propia API de MLflow) para inspeccionarlos. Conviene tenerlo presente al validar que los artefactos se están guardando correctamente: aunque no aparezcan renderizados en la UI, sí están persistidos en el contenedor.

---

## Apéndice: MLflow en DagsHub

[DagsHub](./04_dagshub.md) proporciona un servidor de MLflow gestionado para cada repositorio, lo que evita tener que desplegar y mantener un servidor propio. En ese caso, el *tracking URI* apunta al *endpoint* de MLflow del repositorio de DagsHub, y la autenticación se realiza con el usuario y el *token* de DagsHub en lugar de con credenciales de Azure.

```python
import mlflow

mlflow.set_tracking_uri("https://dagshub.com/<usuario>/<repositorio>.mlflow")
# Autenticación mediante variables de entorno:
#   MLFLOW_TRACKING_USERNAME=<usuario>
#   MLFLOW_TRACKING_PASSWORD=<token>
```

Es una alternativa cómoda para entornos académicos o proyectos pequeños, ya que integra en una sola plataforma el versionado de datos (DVC) y el seguimiento de experimentos (MLflow).

---

## Apéndice: despliegue de un servidor de tracking

Hasta ahora se ha descrito cómo arrancar el servidor con un comando, pero un despliegue real —el "servidor donde levantar MLflow"— requiere decidir tres piezas y cómo se conectan entre sí. Esta sección detalla el montaje completo, tomando como referencia una **VM de Linux** (por ejemplo, en Azure) con **PostgreSQL** como *backend store* y **Azure Blob Storage** como *artifact store*.

### Las tres piezas de un servidor de tracking

1. **El proceso del servidor** (`mlflow server`) — recibe las peticiones de los clientes por HTTP.
2. **El *backend store*** — una base de datos SQL para los metadatos. **El *Model Registry* exige una base de datos** (no funciona con almacenamiento en ficheros), por lo que en un despliegue serio PostgreSQL o MySQL son la opción adecuada, no SQLite.
3. **El *artifact store*** — el *object storage* para los artefactos (Azure Blob Storage en este caso).

El cliente nunca escribe directamente en la base de datos: interactúa siempre con el servidor mediante peticiones REST, y es el servidor quien accede al *backend store*.

### Acceso a artefactos: proxy frente a acceso directo

Existe una decisión de diseño importante sobre **cómo llegan los artefactos al *artifact store***, y determina quién necesita las credenciales de Azure:

- **Acceso *proxied* (recomendado)** — se arranca el servidor con `--artifacts-destination` (y `--serve-artifacts`, activo por defecto). Con esta configuración, **el servidor actúa de intermediario**: los clientes envían y descargan artefactos a través del propio servidor, usando el URI especial `mlflow-artifacts:/`. La gran ventaja es que **solo el servidor necesita las credenciales de Azure**; los clientes no gestionan ningún *token* ni clave.
- **Acceso directo** — se arranca con `--default-artifact-root` y `--no-serve-artifacts`. En este caso **cada cliente sube los artefactos directamente** al *artifact store*, por lo que **todos los clientes necesitan credenciales** de acceso a Azure Blob Storage.

Para un entorno con varios usuarios (como una clase), el acceso *proxied* es claramente preferible: centraliza las credenciales en un único punto y simplifica la configuración de cada cliente.

### Paso 1: preparar el backend store (PostgreSQL)

En la VM, instalar PostgreSQL y crear una base de datos y un usuario dedicados a MLflow:

```bash
sudo apt update && sudo apt install -y postgresql
sudo -u postgres psql
```

Dentro de la consola de PostgreSQL:

```sql
CREATE DATABASE mlflow;
CREATE USER mlflow_user WITH ENCRYPTED PASSWORD 'una_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow_user;
\q
```

### Paso 2: preparar el artifact store (Azure Blob Storage)

Crear (si no existe) un contenedor de blobs en la cuenta de almacenamiento y tener lista la credencial. Como se detalló en la sección de Azure, si la VM dispone de **identidad administrada con rol `Storage Blob Data Contributor`**, `DefaultAzureCredential()` la usará automáticamente y no hará falta configurar claves.

### Paso 3: instalar las dependencias en el servidor

```bash
pip install mlflow psycopg2-binary azure-storage-blob
```

- `mlflow` — el servidor.
- `psycopg2-binary` — controlador de PostgreSQL para el *backend store*.
- `azure-storage-blob` — conector de Azure para el *artifact store*.

### Paso 4: arrancar el servidor

```bash
mlflow server \
  --backend-store-uri postgresql://mlflow_user:una_contraseña_segura@localhost:5432/mlflow \
  --artifacts-destination wasbs://<contenedor>@<cuenta_almacenamiento>.blob.core.windows.net \
  --serve-artifacts \
  --host 0.0.0.0 \
  --port 5000
```

Recuerda que `--host 0.0.0.0` hace que el servidor escuche en todas las interfaces de la VM, condición necesaria para que sea accesible desde otras máquinas (véase el apéndice de redes del documento de Docker sobre `0.0.0.0`).

### Paso 5: ejecutar el servidor de forma persistente

El comando anterior se detiene al cerrar la sesión. Para que el servidor siga vivo de forma permanente:

**Servicio de systemd.** Se define un servicio que arranca MLflow automáticamente y lo reinicia si falla. Se crea `/etc/systemd/system/mlflow.service`:

```ini
[Unit]
Description=MLflow Tracking Server
After=network.target

[Service]
User=mlflow
Environment="AZURE_STORAGE_CONNECTION_STRING=..."
ExecStart=/ruta/al/venv/bin/mlflow server \
  --backend-store-uri postgresql://mlflow_user:una_contraseña_segura@localhost:5432/mlflow \
  --artifacts-destination wasbs://<contenedor>@<cuenta>.blob.core.windows.net \
  --serve-artifacts --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Y se habilita con:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mlflow
```

### Gestión segura de credenciales

Los comandos anteriores incluyen la contraseña de PostgreSQL en texto plano dentro de la URI del *backend store*. **Esto debe evitarse en un despliegue real**, porque esa cadena queda expuesta en el historial de la *shell*, en la lista de procesos (`ps aux`, visible para otros usuarios de la máquina) y en los *logs*.

La regla es: **la credencial nunca en la línea de comandos ni en el código; siempre en una variable de entorno cargada desde un origen protegido**, que a su vez nunca se sube a Git. A continuación se presentan dos niveles.

#### Nivel básico: fichero de entorno con systemd

MLflow lee la URI del *backend store* desde la variable `MLFLOW_BACKEND_STORE_URI`. Se traslada la credencial a un fichero de entorno con permisos restringidos y se referencia desde el servicio de systemd.

**1.** Crear `/etc/mlflow/mlflow.env` con permisos `600` (solo su propietario puede leerlo):

```bash
sudo mkdir -p /etc/mlflow
sudo tee /etc/mlflow/mlflow.env > /dev/null <<'EOF'
MLFLOW_BACKEND_STORE_URI=postgresql://mlflow_user:una_contraseña_segura@localhost:5432/mlflow
EOF
sudo chmod 600 /etc/mlflow/mlflow.env
```

**2.** Referenciarlo en el servicio con `EnvironmentFile`, de modo que el `ExecStart` **ya no contenga la credencial**:

```ini
[Service]
User=mlflow
EnvironmentFile=/etc/mlflow/mlflow.env
ExecStart=/ruta/al/venv/bin/mlflow server \
  --artifacts-destination wasbs://<contenedor>@<cuenta>.blob.core.windows.net \
  --serve-artifacts --host 0.0.0.0 --port 5000
Restart=always
```

La contraseña vive ahora en un fichero protegido y fuera del control de versiones, no en la invocación.

#### Nivel avanzado: gestor de secretos (Azure Key Vault)

En un entorno con exigencias de seguridad, la credencial no se guarda ni siquiera en un fichero en disco, sino en un **gestor de secretos** del que el servidor la recupera al arrancar. En Azure, el servicio natural es **Azure Key Vault**, y encaja especialmente bien porque puede autenticarse con la **misma identidad administrada de la VM** que ya se usa para el *artifact store*, sin claves adicionales.

**1. Crear el Key Vault** (una vez):

```bash
az keyvault create \
  --name <nombre_keyvault> \
  --resource-group <grupo_recursos> \
  --location <region>
```

**2. Guardar la credencial como secreto:**

```bash
az keyvault secret set \
  --vault-name <nombre_keyvault> \
  --name mlflow-backend-uri \
  --value "postgresql://mlflow_user:una_contraseña_segura@localhost:5432/mlflow"
```

**3. Autorizar a la identidad administrada de la VM** a leer secretos del Key Vault. Se asigna el rol de plano de datos **`Key Vault Secrets User`** a la identidad de la VM sobre el *scope* del Key Vault:

```bash
az role assignment create \
  --assignee <id_identidad_administrada> \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show --name <nombre_keyvault> --query id -o tsv)
```

> Igual que con el *artifact store*, el rol debe ser el de **plano de datos** (`Key Vault Secrets User`), que concede acceso a *leer los secretos*; los roles de gestión del *vault* no bastan para leer su contenido.

**4. Recuperar el secreto en el arranque** mediante un pequeño *script* que la VM ejecuta autenticándose con su identidad administrada. Se crea `/usr/local/bin/start-mlflow.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Autenticación con la identidad administrada de la VM (sin claves)
az login --identity --allow-no-subscriptions >/dev/null

# Recuperar el secreto y exportarlo como variable de entorno
export MLFLOW_BACKEND_STORE_URI="$(az keyvault secret show \
  --vault-name <nombre_keyvault> \
  --name mlflow-backend-uri \
  --query value -o tsv)"

# Arrancar el servidor (la credencial nunca toca el disco ni la línea de comandos)
exec /ruta/al/venv/bin/mlflow server \
  --artifacts-destination wasbs://<contenedor>@<cuenta>.blob.core.windows.net \
  --serve-artifacts --host 0.0.0.0 --port 5000
```

```bash
sudo chmod 750 /usr/local/bin/start-mlflow.sh
```

**5. Apuntar el servicio de systemd al *script*** en lugar de al comando directo:

```ini
[Service]
User=mlflow
ExecStart=/usr/local/bin/start-mlflow.sh
Restart=always
```

Con este enfoque, la contraseña **nunca está escrita en la máquina**: se obtiene bajo demanda desde el Key Vault en cada arranque, el acceso queda auditado, y la autenticación se apoya en la identidad administrada de la VM, sin claves adicionales que gestionar. Además, rotar la credencial consiste únicamente en actualizar el secreto en el Key Vault, sin tocar la configuración del servidor.

> **Nota:** este *script* requiere tener instalada la CLI de Azure (`az`) en la VM. El mismo patrón puede implementarse con el SDK de Azure (`azure-keyvault-secrets` + `azure-identity`) desde un envoltorio en Python, si se prefiere no depender de la CLI.

### Paso 6: seguridad (imprescindible si se expone)

Por defecto, **el servidor de MLflow no incluye autenticación**: cualquiera que alcance su puerto puede leer y escribir experimentos. Antes de exponerlo más allá de la propia red conviene:

- Situarlo detrás de un **reverse proxy** (nginx) que añada **HTTPS** y **autenticación básica** (usuario/contraseña).
- O bien habilitar la **autenticación integrada** de MLflow (funcionalidad más reciente, basada en usuarios y permisos).
- Restringir el acceso a nivel de red. Ligando con lo visto sobre Azure: no abrir el puerto 5000 en el NSG salvo que sea necesario; para acceso personal basta con el reenvío de puertos por SSH.

### Paso 7: configurar el cliente

Finalmente, en el código de entrenamiento se apunta al servidor. Con acceso *proxied*, el cliente **no necesita credenciales de Azure**:

```python
import mlflow

mlflow.set_tracking_uri("http://<ip_de_la_vm>:5000")
mlflow.set_experiment("mi_experimento")

with mlflow.start_run():
    mlflow.log_metric("accuracy", 0.94)
    mlflow.log_artifact("resultados.png")   # sube al servidor, que lo reenvía a Azure
```

---

## Apéndice: reverse proxy y certificados

El paso 6 del despliegue recomendaba situar el servidor de MLflow **detrás de un reverse proxy** con HTTPS y autenticación. Esta sección explica ambos conceptos, ya que son la base de casi cualquier despliegue web seguro.

### Qué es un reverse proxy

Un **reverse proxy** (proxy inverso) es un servidor que se coloca **delante** de uno o varios servidores y actúa como **intermediario**: recibe las peticiones de los clientes y las reenvía al servidor interno que corresponde, devolviendo después la respuesta. El cliente solo ve el proxy; nunca contacta directamente con el servidor de detrás.

Sirve de analogía la **recepción de un hotel**: el visitante no acude directamente a las habitaciones, sino que habla con recepción, que filtra quién pasa y enruta cada petición a quien corresponde.

El flujo de una petición es el siguiente:

```
[Cliente] → https://mlflow.miempresa.com → [Reverse Proxy] → localhost:5000 → [MLflow]
                                                (nginx)
[Cliente] ←──────────── respuesta ─────────── ←──────────────────────────────
```

El servidor de MLflow permanece en `localhost:5000`, sin exponerse a internet; solo el proxy le habla. Las funciones principales que aporta el reverse proxy son:

- **Terminación de HTTPS/TLS** — gestiona el cifrado (presenta el certificado, cifra y descifra), de modo que el servidor de detrás puede seguir hablando HTTP plano en local. Resuelve la carencia de HTTPS de MLflow.
- **Autenticación** — exige credenciales *antes* de dejar pasar la petición. Como MLflow no incluye autenticación por defecto, el proxy hace de portero.
- **Protección** — el servidor real no queda expuesto directamente; se reduce la superficie de ataque.
- **Balanceo de carga** — si hay varias instancias del servidor, reparte las peticiones entre ellas.
- **Enrutamiento** — puede dirigir distintas rutas o dominios a distintos servicios bajo un único punto de entrada.

> **Reverse proxy frente a *forward proxy*:** un *forward proxy* se sitúa delante de los **clientes** (representa a quien hace las peticiones); un *reverse proxy* se sitúa delante de los **servidores** (representa a quien las recibe). De ahí el "inverso".

### Instalación de nginx

En una VM de Linux (Ubuntu/Debian), nginx se instala desde los repositorios de la distribución:

```bash
sudo apt update
sudo apt install -y nginx
```

El servicio se gestiona con systemd y conviene habilitarlo para que arranque con el sistema:

```bash
sudo systemctl enable --now nginx
sudo systemctl status nginx      # comprobar que está activo
```

Además, la utilidad `htpasswd` (usada más abajo para la autenticación) viene en un paquete aparte:

```bash
sudo apt install -y apache2-utils
```

### Dónde vive cada fichero de configuración

Es importante saber **dónde va cada cosa**, porque nginx reparte su configuración en varios directorios con una convención clara:

| Ruta | Contenido |
|---|---|
| `/etc/nginx/nginx.conf` | Configuración **global** de nginx. Normalmente no se toca; incluye automáticamente los ficheros de los directorios de abajo. |
| `/etc/nginx/sites-available/` | Ficheros de configuración de **cada sitio** (los `server { ... }`). Aquí se **crea** la config de MLflow, pero estar aquí **no** la activa. |
| `/etc/nginx/sites-enabled/` | Sitios **activos**. Se activan creando un **enlace simbólico** desde `sites-available`. nginx solo sirve lo que está aquí. |
| `/etc/nginx/ssl/` | Ubicación habitual (creada por el usuario) para los **certificados y claves privadas**. Con Let's Encrypt, en cambio, van a `/etc/letsencrypt/live/<dominio>/`. |
| `/etc/nginx/.htpasswd` | Fichero de **usuarios y contraseñas** de la autenticación básica. |
| `/var/log/nginx/` | *Logs* de acceso (`access.log`) y de error (`error.log`). |

> **Nota:** en distribuciones basadas en RHEL (Fedora, CentOS, Rocky) no existe el par `sites-available` / `sites-enabled`; en su lugar se colocan los ficheros directamente en `/etc/nginx/conf.d/` con extensión `.conf`. El contenido del `server { ... }` es el mismo.

### Ejemplo con nginx delante de MLflow

La siguiente configuración se guarda en **`/etc/nginx/sites-available/mlflow`**. Escucha en HTTPS (puerto 443), exige autenticación básica y reenvía todo el tráfico a MLflow en local. Incluye además un segundo bloque que **redirige HTTP (puerto 80) a HTTPS**, para que nadie acceda sin cifrar:

```nginx
# Redirección de HTTP a HTTPS
server {
    listen 80;
    server_name mlflow.miempresa.com;
    return 301 https://$host$request_uri;
}

# Servidor HTTPS con autenticación, que hace de proxy hacia MLflow
server {
    listen 443 ssl;
    server_name mlflow.miempresa.com;

    # Certificado y clave privada para HTTPS
    ssl_certificate     /etc/nginx/ssl/mlflow.crt;
    ssl_certificate_key /etc/nginx/ssl/mlflow.key;

    # Autenticación básica: exige usuario y contraseña
    auth_basic           "Acceso restringido a MLflow";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:5000;      # reenvía a MLflow
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

El fichero de usuarios para `auth_basic` se genera en **`/etc/nginx/.htpasswd`** con la utilidad `htpasswd` (la opción `-c` crea el fichero; omítela para **añadir** usuarios a uno existente, o lo sobrescribirías):

```bash
sudo htpasswd -c /etc/nginx/.htpasswd <usuario>
```

### Activar la configuración

Crear la config en `sites-available` **no la activa**: hay que enlazarla en `sites-enabled`, comprobar la sintaxis y recargar nginx.

```bash
# 1. Activar el sitio (enlace simbólico de sites-available a sites-enabled)
sudo ln -s /etc/nginx/sites-available/mlflow /etc/nginx/sites-enabled/

# 2. (Opcional) desactivar el sitio por defecto que trae nginx
sudo rm /etc/nginx/sites-enabled/default

# 3. Comprobar que la configuración no tiene errores de sintaxis
sudo nginx -t

# 4. Aplicar los cambios sin cortar las conexiones existentes
sudo systemctl reload nginx
```

El paso 3 (`nginx -t`) es importante: valida la configuración **antes** de aplicarla, de modo que un error de sintaxis no tumbe el servicio. Si `nginx -t` da error, corrígelo antes de recargar.

Con esta configuración, MLflow sigue corriendo en `127.0.0.1:5000` sin cifrado ni autenticación propios, y nginx le añade por delante el HTTPS y el control de acceso que le faltaban.

> Herramientas equivalentes a nginx para esta función son **Traefik**, **HAProxy** y **Caddy** (este último gestiona los certificados HTTPS de forma automática).

### Obtener un certificado con Let's Encrypt (opcional)

Si el servidor es accesible públicamente con un dominio propio, en lugar de indicar manualmente el `ssl_certificate` se puede usar **certbot**, que obtiene un certificado gratuito de Let's Encrypt y **configura nginx automáticamente**:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d mlflow.miempresa.com
```

certbot edita el fichero del sitio para añadir las rutas correctas de `ssl_certificate` (que quedarán en `/etc/letsencrypt/live/mlflow.miempresa.com/`) y programa la renovación automática. En ese caso no hace falta el directorio `/etc/nginx/ssl/` ni gestionar los certificados a mano.

### Cómo funcionan los certificados (TLS/SSL)

El HTTPS del ejemplo se apoya en un **certificado**. Un certificado TLS resuelve dos problemas a la vez: **cifrar** la comunicación y **verificar la identidad** del servidor (que `mlflow.miempresa.com` es de verdad quien dice ser, y no un impostor).

**1. Criptografía asimétrica (la base).** Cada servidor tiene un **par de claves** matemáticamente relacionadas:

- Una **clave privada**, que se mantiene en secreto en el servidor (el fichero `.key` del ejemplo).
- Una **clave pública**, que se distribuye libremente.

Lo que se cifra con una de ellas solo puede descifrarse con la otra. Esto permite que cualquiera cifre un mensaje con la clave pública del servidor, sabiendo que **solo** el poseedor de la clave privada podrá leerlo.

**2. El certificado en sí.** Un certificado es, en esencia, la **clave pública del servidor acompañada de su identidad** (el dominio, la organización), todo ello **firmado por una autoridad de confianza**. Es el equivalente digital de un carné de identidad: no basta con que alguien diga quién es; hace falta que un organismo reconocido lo avale.

**3. La cadena de confianza (Certificate Authorities).** Ese "organismo reconocido" es una **Autoridad de Certificación** (CA): entidades en las que los navegadores y sistemas operativos confían de fábrica (traen preinstalada una lista de CA raíz). Cuando una CA firma el certificado de un servidor, está garantizando que verificó su identidad. El navegador razona así: *"No conozco a este servidor, pero su certificado está firmado por una CA en la que sí confío, así que lo doy por válido"*. Es una **cadena de confianza**: se confía en el servidor porque se confía en quien lo avala.

**4. El *handshake* TLS (qué ocurre al conectar).** De forma simplificada, al abrir `https://...`:

1. El cliente solicita conexión segura; el servidor le envía su **certificado** (con su clave pública).
2. El cliente **verifica** el certificado: comprueba que lo firma una CA de confianza, que no ha caducado y que el dominio coincide.
3. Si es válido, ambos **negocian una clave de sesión** (simétrica, más rápida) usando la criptografía asimétrica para intercambiarla de forma segura.
4. A partir de ahí, toda la comunicación viaja **cifrada** con esa clave de sesión.

El resultado es el candado del navegador: identidad verificada y tráfico cifrado.

### Tipos de certificado según el origen

- **Certificados de una CA pública (p. ej. Let's Encrypt).** Emitidos por una CA reconocida y **gratuitos** en el caso de Let's Encrypt, que además automatiza la renovación (con herramientas como `certbot`). Son la opción adecuada para un servicio **accesible desde internet con un dominio propio**, porque los navegadores los aceptan sin advertencias.
- **Certificados autofirmados (*self-signed*).** El propio servidor firma su certificado, sin CA externa. Cifran igual, pero **ninguna CA avala la identidad**, así que los navegadores muestran una advertencia de seguridad. Son válidos para **entornos internos o de pruebas**, donde el acceso es controlado y la advertencia es asumible.

> Para un servidor de MLflow accesible públicamente, lo recomendable es un certificado de Let's Encrypt. Para uno de uso interno (solo alcanzable por la red privada o por túnel SSH), un certificado autofirmado suele ser suficiente.

---

## Apéndice: instalación de MLflow

MLflow se distribuye como un paquete de Python y se instala con `pip`. Se recomienda hacerlo dentro de un **entorno virtual** (por ejemplo `venv` o Conda) para aislar las dependencias del proyecto.

### Instalación básica

```bash
pip install mlflow
```

Esto instala MLflow completo, incluyendo la interfaz web (UI), la CLI y las dependencias necesarias para el *tracking*, los *projects*, los *models* y el *registry*.

### Verificar la instalación

```bash
mlflow --version
```

### Variante ligera

Para entornos donde solo se necesita el registro de experimentos sin la UI ni componentes pesados (por ejemplo, dentro de un contenedor de entrenamiento), existe una variante reducida:

```bash
pip install mlflow-skinny
```

### Dependencias adicionales según el almacenamiento

MLflow no incluye por defecto los conectores de todos los almacenamientos remotos; deben instalarse aparte según el *artifact store* que se vaya a usar:

- **Azure Blob Storage:** `pip install azure-storage-blob` (véase la sección de Azure de este documento).
- **Amazon S3:** `pip install boto3`.
- **Google Cloud Storage:** `pip install google-cloud-storage`.

Igualmente, si el *backend store* es una base de datos SQL, se instala el controlador correspondiente (p. ej. `pip install psycopg2-binary` para PostgreSQL).

### Arranque rápido en local

Para lanzar la interfaz web con la configuración por defecto (metadatos y artefactos en el directorio local `./mlruns`):

```bash
mlflow ui
```

Por defecto queda accesible en `http://127.0.0.1:5000`. Para un servidor de *tracking* con almacenamiento remoto, se emplea `mlflow server` con los parámetros descritos en la sección anterior.

> **Nota:** `mlflow ui` está pensado para uso local y desarrollo, mientras que `mlflow server` es la opción para desplegar un servidor de *tracking* compartido con *backend* y *artifact store* remotos.
