# Arquitectura de Microservicios

La **arquitectura de microservicios** es un enfoque de diseño de software en el que una aplicación se estructura como un conjunto de servicios pequeños, autónomos y desplegables de forma independiente, que se comunican entre sí mediante APIs o mensajes.

## Características principales

- **Responsabilidad única:** cada microservicio es responsable de una funcionalidad específica.
- **Despliegue independiente:** cada servicio se puede actualizar sin afectar a los demás.
- **Heterogeneidad tecnológica:** se pueden emplear diferentes lenguajes, bases de datos o herramientas en cada microservicio.
- **Escalabilidad granular:** se escalan únicamente los servicios que lo necesitan.
- **Bajo acoplamiento:** los servicios no dependen directamente entre sí.

## Componentes de una arquitectura de microservicios

Al diseñar una arquitectura de microservicios, los componentes principales son:

- **Microservicios** — los servicios que implementan la lógica de negocio.
  - *Python → FastAPI:* framework web moderno, rápido y eficiente para construir APIs con Python 3.7+, basado en el tipado estático (*type hints*) y en estándares como OpenAPI y JSON Schema.
- **API Gateway** — punto de entrada único que recibe las peticiones externas y las enruta al microservicio correspondiente.
- **Service Discovery** — mecanismo que permite a los servicios localizarse entre sí de forma dinámica, sin depender de direcciones fijas.
- **Mensajería** — comunicación asíncrona entre servicios mediante colas o eventos (p. ej. RabbitMQ, Kafka).
- **Contenerización y orquestación** — empaquetado de los servicios y gestión centralizada de su ciclo de vida.
  - [**Docker**](./06_docker.md): plataforma de código abierto que permite empaquetar aplicaciones y sus dependencias en contenedores, facilitando su despliegue y ejecución en cualquier entorno.
- **Monitorización** — observabilidad del sistema mediante métricas, *logs* y trazas.
- **Seguridad** — autenticación, autorización y cifrado de las comunicaciones entre servicios.
- **Orquestación de *workflows*** — coordinación de procesos que abarcan varios microservicios.
