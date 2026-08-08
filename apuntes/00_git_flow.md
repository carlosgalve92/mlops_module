# Git Flow en MLOps

> Estrategia de ramas y ciclo de trabajo para sistemas de Machine Learning en producción.

El **Git Flow** en un sistema de *Machine Learning* (ML) sigue una estructura similar a la del desarrollo de software tradicional, pero incorpora particularidades propias de la naturaleza de los modelos, los experimentos y los datos. A continuación se describe un flujo de **MLOps en producción**.

---

## 1. Estrategia de ramas

### 1.1 Ramas principales

| Rama | Propósito |
|---|---|
| **`master` / `main`** | Contiene la última versión **estable** del sistema de ML en producción. |
| **`develop`** | Contiene el código en desarrollo que se integrará en `master` tras pruebas y validaciones. |

### 1.2 Ramas auxiliares

| Rama | Se crea desde | Se fusiona en | Propósito |
|---|---|---|---|
| **`feature/<nombre>`** | `develop` | `develop` | Desarrollar nuevas funcionalidades o mejorar el código. |
| **`experiment/<nombre>`** | `feature` / `develop` | `develop` (si el experimento es exitoso) | Probar modelos y realizar experimentos de ML sin afectar el código estable. |
| **`release/<nombre>`** | `develop` | `master` y `develop` | Preparar y estabilizar nuevas versiones antes de producción. |
| **`hotfix/<nombre>`** | `master` | `master` y `develop` | Corregir errores críticos en producción de forma urgente. |

---

## 2. Ciclo de desarrollo

```
                    ┌─────────────┐
                    │   master    │◄──── release ────┐◄──── hotfix
                    └──────┬──────┘                  │         │
                           │                         │         ▼
                    ┌──────▼──────┐            ┌──────┴──────────────┐
                    │   develop   │◄─ feature ─┤  experiment (MLflow) │
                    └─────────────┘            └──────────────────────┘
                          ▲
                          └── DVC (versionado de datos)
```

**Paso 1 — Crear una rama `feature`.**
Se desarrolla la nueva funcionalidad sin afectar a `master` ni a `develop`.

- **1.1** Se realizan experimentos en ramas `experiment`. Si el experimento tiene éxito, la rama se fusiona en `develop`.
  - Con **MLflow** se registran hiperparámetros, métricas y artefactos.
- **1.2** Se versionan los datos con **DVC**.

**Paso 2 — Fusionar `feature` en `develop`.**
Así `develop` mantiene siempre las últimas mejoras antes de un lanzamiento.

- **2.1** Se ejecutan las pruebas de **CI/CD** antes de fusionar.

**Paso 3 — Crear una rama `release`.**
Se estabiliza el código antes de llevarlo a producción: se ajusta la documentación y se realizan las pruebas finales para preparar el despliegue.

**Paso 4 — Fusionar `release` en `master`.**
Se despliega en producción.

- **4.1** Se ejecutan las pruebas de **CI/CD** antes de fusionar.

**Paso 5 — Gestionar incidencias con `hotfix`.**
Si aparece un error en `master`, se crea una rama `hotfix` para una corrección rápida, que luego se fusiona **tanto en `master` como en `develop`**.

> [!IMPORTANT]
> El `hotfix` debe fusionarse en **ambas** ramas. Si solo se lleva a `master`, la corrección se perdería en el siguiente lanzamiento desde `develop`.

---

## 3. Herramientas del flujo

Este material se organiza en los siguientes módulos:

| Módulo | Herramienta | Rol en el flujo |
|---|---|---|
| **[Git](01_git.md)** | Control de versiones | Versionado local del código. |
| **[GitHub](02_github.md)** | Repositorio remoto | Colaboración y sincronización en la nube. |
| **[DVC](03_dvc.md)** | *Data Version Control* | Versionado de datos y modelos. |
| **[DagsHub](04_dasghub.md)** | Plataforma MLOps | Integración de Git, DVC y MLflow en un mismo lugar. |

---

### Empieza por

➡️ **[Git](01_git.md)** — la base del flujo de trabajo.
