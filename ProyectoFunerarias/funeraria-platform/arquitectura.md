# Documento de Arquitectura de Software
## Plataforma Funerarias Multi-Tenant (SaaS)

Este documento describe formalmente la arquitectura de software de la **Plataforma Funerarias**, analizando su estructura de directorios, patrones arquitectónicos implementados, la viabilidad del modelo de vistas 4+1 y los flujos clave que describen el sistema en su totalidad.

---

## 1. Análisis de la Estructura de Carpetas del Proyecto

El proyecto está organizado en un monorepositorio estructurado que separa claramente las responsabilidades del frontend, backend e infraestructura local. A continuación, se detalla la estructura principal:

```
ProyectoFunerarias/
└── funeraria-platform/
    ├── docker-compose.yml       # Orquestador de contenedores (topología física)
    ├── backend/                 # Backend REST API (Flask en Python)
    │   ├── app.py               # Punto de entrada de la aplicación backend
    │   ├── config.py            # Parámetros de configuración (variables de entorno)
    │   ├── middleware/          # Middlewares (ej. extracción del tenant_id)
    │   ├── modules/             # Capa de lógica de negocio modular por blueprints
    │   │   ├── auth/            # Módulo de integración con Keycloak
    │   │   ├── admin/           # Administración del catálogo y usuarios del tenant
    │   │   ├── superadmin/      # Administración global del sistema
    │   │   ├── kafka/           # Eventos del productor de Apache Kafka
    │   │   └── public/          # Rutas públicas (catálogo y contacto)
    │   └── utils/               # Utilidades comunes (ej. conexión a MongoDB)
    ├── frontend/                # Frontend SPA (Angular 17+)
    │   ├── angular.json         # Configuración del build (file replacements por tenant)
    │   ├── Dockerfile.central   # Build específico para el tenant "Central"
    │   ├── Dockerfile.eternidad # Build específico para el tenant "La Eternidad"
    │   ├── Dockerfile.losolivos  # Build específico para el tenant "Los Olivos"
    │   └── src/
    │       ├── environments/    # Configuración de entornos y variables por tenant
    │       └── app/
    │           ├── core/        # Servicios, guards e interceptores compartidos de la app
    │           ├── shared/      # Componentes visuales y tuberías reutilizables
    │           └── modules/     # Módulos de funcionalidad (auth, admin, catalog, home)
    └── keycloak/                # Datos de inicio e integración de Identity Provider (IAM)
        └── seedKey.json         # Configuración del Realm y Clientes de Keycloak
```

---

## 2. Las 2 Arquitecturas que se Adaptan al Proyecto

Basado en el análisis de código y diseño del proyecto, las dos arquitecturas predominantes que definen y guían el comportamiento del sistema son:

### A. Arquitectura Multi-Tenant (Multi-inquilino) del tipo "Shared Database, Shared Schema"
El sistema está diseñado como una plataforma SaaS (Software as a Service) donde múltiples funerarias (tenants) comparten la misma infraestructura de backend y base de datos, pero con un aislamiento lógico estricto.

* **Puntos clave de por qué aplica:**
  1. **Frontend con Multi-Instancia y Reemplazo de Entornos:** En [`angular.json`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/frontend/angular.json), el sistema define configuraciones independientes para cada tenant (`eternidad`, `losolivos`, `central`). Cada build reemplaza el archivo genérico `environment.ts` por uno específico (ej. [`environment.eternidad.ts`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/frontend/src/environments/environment.eternidad.ts)) que inyecta parámetros visuales (colores primarios/secundarios, títulos y logotipos).
  2. **Resolución Dinámica del Tenant en Frontend:** El servicio [`tenant.ts`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/frontend/src/app/core/services/tenant.ts) implementa la lógica para aplicar dinámicamente el tema visual mediante propiedades CSS personalizadas (`--primary-color`, `--secondary-color`) en el DOM raíz (`document.documentElement`).
  3. **Middleware de Aislamiento Lógico en Backend:** En [`tenant.py`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/middleware/tenant.py), se intercepta cada petición API para descifrar el token JWT de Keycloak, buscar el usuario en MongoDB y adjuntar el `tenant_id` al contexto global del request (`g.tenant_id`).
  4. **Persistencia Compartida Filtrada por Discriminador:** Los servicios de base de datos (ej. [`services.py`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules/admin/services.py)) siempre consultan la base de datos MongoDB incluyendo de forma obligatoria el discriminador `{"tenant_id": ObjectId(tenant_id)}`. Esto evita fugas de información (*data leaks*) entre funerarias de forma transparente.

### B. Arquitectura Basada en Eventos (Event-Driven Architecture) & Estructura de Tres Capas (3-Tier)
La aplicación web utiliza la arquitectura clásica de tres capas para estructurar el software internamente, pero incorpora un patrón de comunicación asíncrona dirigido por eventos utilizando Apache Kafka para desacoplar transacciones y notificaciones.

* **Puntos clave de por qué aplica:**
  1. **Estructuración Desacoplada (3-Tier):**
     * **Capa de Presentación:** El frontend de Angular compilado y servido de manera autónoma con Nginx.
     * **Capa de Lógica (Negocio):** La API Flask, modularizada bajo subcarpetas que encapsulan rutas, lógica de servicios y validaciones.
     * **Capa de Datos:** Colecciones lógicamente aisladas en MongoDB y persistencia relacional SQL para Keycloak en PostgreSQL.
  2. **Emisión de Eventos Críticos:** Rutas de negocio clave como la creación de productos ([`catalog_routes.py`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules/admin/catalog_routes.py)) o el envío de formularios de contacto por clientes externos ([`routes.py`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules/public/routes.py)) no realizan tareas bloqueantes o síncronas pesadas (como envíos de correo en vivo). En su lugar, publican mensajes en tópicos de Kafka (`product-events`, `contact-events`) mediante el [`producer.py`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules/kafka/producer.py). Esto abre el camino para que otros microservicios o sistemas procesen las notificaciones sin recargar el hilo del backend principal.

---

## 3. Aplicación de la Arquitectura 4+1 en este Proyecto

El modelo de vistas **4+1 de Kruchten** es **totalmente aplicable** y muy útil para este proyecto, ya que el sistema tiene una complejidad de integración notable (múltiples bases de datos, pasarela de eventos, proveedor de identidad externo y compilación de frontends multi-marca).

A continuación se detalla cómo aplica cada una de las vistas de este modelo:

### A. Vista Lógica (Logical View)
*Se enfoca en la funcionalidad que el sistema proporciona a los usuarios finales.*
* **Aplicabilidad en el proyecto:**
  * **Modelo de Dominio Multi-tenant:** Representa cómo las entidades como `Product`, `User`, `Tenant` y `ContactMessage` se relacionan lógicamente. Todos los recursos del catálogo y mensajes de contacto pertenecen de manera estricta a un único `Tenant`.
  * **Control de Acceso Basado en Roles (RBAC):** Define la jerarquía de usuarios.
    * **Superadmin:** Administrador global que gestiona la creación de nuevos tenants (funerarias) a través del módulo [`superadmin`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules/superadmin).
    * **Admin (Tenant Admin):** Encargado de gestionar los productos, configurar colores/cuentas y dar de alta usuarios específicos dentro de su propia funeraria.
    * **Público/Cliente:** Navega por los catálogos públicos y envía mensajes de contacto sin autenticación.

### B. Vista de Proceso (Process View)
*Se enfoca en el comportamiento dinámico del sistema a nivel de ejecución, flujos, rendimiento y sincronización.*
* **Aplicabilidad en el proyecto:**
  * **Flujo de Autenticación y Autorización SSO (Single Sign-On):**
    1. El usuario interactúa con Angular e ingresa sus credenciales en Login.
    2. El frontend se comunica con Keycloak para obtener el token JWT de acceso.
    3. Para consultas posteriores, Angular incluye el token Bearer JWT.
    4. El middleware `extract_tenant` intercepta la petición HTTP, verifica el token contra Keycloak (`kc.verify_token`), busca al usuario en MongoDB local, inyecta los datos de rol y `tenant_id` en el objeto global `g`, permitiendo que la lógica del servicio responda de forma segura.
  * **Flujo de Eventos Asíncronos:** La API de Flask publica eventos en Apache Kafka asíncronamente a través de un productor singleton (`KafkaEventProducer`), liberando de inmediato al hilo HTTP mientras Kafka distribuye el evento.

### C. Vista de Desarrollo / Implementación (Development View)
*Muestra la organización del código fuente, librerías, dependencias y modularidad desde la perspectiva del programador.*
* **Aplicabilidad en el proyecto:**
  * **Modularidad del Backend (Flask Blueprints):** La carpeta [`modules`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/backend/modules) divide limpiamente las funcionalidades por dominios lógicos independientes, facilitando que múltiples desarrolladores trabajen en paralelo.
  * **Organización del Frontend (Angular Clean Architecture):**
    * `core/`: Contiene la lógica del núcleo del sistema como guards de autenticación e interceptores HTTP que añaden encabezados de tenant y token.
    * `shared/`: Contiene elementos visuales comunes a toda la aplicación.
    * `modules/`: Módulos perezosos (*Lazy loaded*) por vistas (Login, Admin, Catálogo) para optimizar el tiempo de carga del navegador.

### D. Vista Física / Despliegue (Physical View)
*Describe la topología de la infraestructura física, servidores, contenedores y la comunicación en red de hardware.*
* **Aplicabilidad en el proyecto:**
  * Está completamente modelada en el archivo [`docker-compose.yml`](file:///g:/Ingenier%C3%ADa/9-%20Noveno%20Semestre%202026-I/Electiva%20II%20Arquitectura/PROYECTO%20REAL/FUNERARIAS-MT/ProyectoFunerarias/funeraria-platform/docker-compose.yml).
  * Consiste en **7 servicios independientes** conectados bajo una misma red privada virtual de Docker (`funeraria_net`):
    1. `mongodb` (Port 27017): Base de datos principal de la plataforma.
    2. `postgres` (Port 5432): Base de datos relacional para la persistencia de Keycloak.
    3. `keycloak` (Port 8080): Servidor de autorización y gestión de accesos (IAM).
    4. `kafka` (Port 9092): Broker de mensajería asíncrona.
    5. `kafka-ui` (Port 8088): Interfaz web para monitorizar tópicos y eventos.
    6. `backend` (Port 5000): Servidor Flask REST API que une todas las piezas.
    7. `frontend-eternidad` / `frontend-losolivos` / `frontend-central` (Puertos 4201, 4202, 4203): Tres contenedores Nginx sirviendo las compilaciones personalizadas de cada funeraria.

### E. Escenarios (Use Cases / +1 View)
*La vista que integra a todas las demás mostrando cómo colaboran los componentes en casos de uso de negocio reales.*
* **Ejemplo de Escenario: "Crear un nuevo producto en el catálogo"**
  ```mermaid
  sequenceDiagram
      autonumber
      actor Admin as Administrador Funeraria
      participant FE as Frontend Angular (Nginx)
      participant KC as Keycloak (IAM)
      participant BE as Backend Flask (API)
      participant DB as MongoDB (Data)
      participant KF as Apache Kafka (Events)

      Admin->>FE: Introduce datos del producto y da clic en "Guardar"
      FE->>BE: POST /api/admin/products (Headers: Bearer JWT)
      Note over BE: El middleware extract_tenant extrae el token,<br/>obtiene el tenant_id de MongoDB y lo almacena en g.tenant_id
      BE->>DB: AdminService.create_product(tenant_id, datos)
      DB-->>BE: Retorna producto guardado con tenant_id
      BE->>KF: publicar evento 'product_created' en topic 'product-events'
      KF-->>BE: Confirmación de recepción asíncrona (delivery report)
      BE-->>FE: HTTP 201 (JSON con el producto creado)
      FE-->>Admin: Muestra el producto en el catálogo administrador
  ```

---

## 4. Conclusiones y Explicación del Software en su Totalidad

La plataforma funeraria está diseñada bajo una **filosofía ágil, modular y multi-inquilino**. 

* **Flujo del Negocio Principal:** El software permite que cualquier funeraria adquiera un portal web personalizado con su identidad corporativa sin necesidad de desarrollar un sitio web desde cero. 
* **Seguridad Robusta:** La integración con Keycloak garantiza que las contraseñas, roles y sesiones estén gobernados por un estándar industrial (OAuth2 / OIDC). 
* **Modularidad y Futuro Extensible:** La inclusión de Kafka prepara el sistema para evolucionar fácilmente hacia una arquitectura de microservicios, donde módulos pesados como facturación o notificaciones por SMS/correo puedan implementarse en diferentes lenguajes y escalar de forma independiente.
* **Eficiencia de Persistencia:** Al utilizar un diseño de base de datos NoSQL compartida con discriminador lógico (`tenant_id`), los costos de infraestructura se minimizan drásticamente mientras se mantiene un esquema de datos altamente elástico para los catálogos variables de productos funerarios.
