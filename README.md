# Funeraria-Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue)](#)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey)](#)
[![Angular](https://img.shields.io/badge/Angular-17-red)](#)
[![MongoDB](https://img.shields.io/badge/MongoDB-7-green)](#)
[![Docker](https://img.shields.io/badge/Docker-24.0.5-blue)](#)
[![Keycloak](https://img.shields.io/badge/Keycloak-24.0-orange)](#)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-3.6-black)](#)

Plataforma web multitenant para la exhibición de servicios exequiales y gestión de funerarias, desarrollada con **Flask**, **Angular 17**, **MongoDB**, **Keycloak** y **Apache Kafka**, completamente contenerizada con **Docker**.

---

## Tecnologías Utilizadas

* **Backend:**
    * Python 3.12
    * Flask 3.1.0 (Blueprints REST API)
    * PyMongo (MongoDB driver)
    * Flask-CORS
    * python-jose (validación de tokens JWT)
    * Keycloak Admin REST API
    * librdkafka (cliente Python `confluent-kafka` para Apache Kafka)
* **Frontend:**
    * Angular 17 (lazy loading modules)
    * TypeScript
    * RxJS
    * Angular Router
    * CSS custom properties (temas dinámicos por tenant)
* **Base de Datos:**
    * MongoDB 7 (documentos con discriminación por tenant)
    * Colecciones: `tenants`, `users`, `products`, `contacts`
* **Infraestructura:**
    * Docker + Docker Compose (6 servicios + redes)
    * Nginx (servidor web para frontend)
    * Gunicorn (servidor WSGI para backend)
* **Seguridad y Mensajería:**
    * Keycloak 24.0 (Identity Provider, OIDC, JWT, roles)
    * Apache Kafka 3.6 (bus de eventos)
    * Kafka UI (monitoreo de tópicos)

---

## Características

* **Arquitectura Multitenant:**
    * Aislamiento de datos por `tenant_id` en todas las colecciones de MongoDB.
    * Identificación del tenant por slug (subdominio o query param).
    * Middleware Flask que inyecta `g.tenant_id`, `g.user_id` y `g.role`.
* **Portal público personalizado:**
    * Página de inicio, Quiénes somos, Servicios/Membresías/Convenios.
    * Catálogo de arreglos florales con precios y ataúdes sin precios.
    * Formulario de contacto con envío de mensajes al correo del tenant.
    * Redirección a WhatsApp con número configurable.
    * CSS dinámico: colores y logo adaptados al tenant.
* **Panel de administración con roles:**
    * Admin: configuración visual (logo, colores, datos de contacto), CRUD de productos, edición de precios, creación de usuarios operarios.
    * Operario: CRUD de productos, sin acceso a precios ni a usuarios.
    * Autenticación delegada en Keycloak (JWT, roles de realm).
* **Eventos de dominio en tiempo real (Kafka):**
    * Tópicos: `auth-events`, `product-events`, `config-events`, `contact-events`, `tenant-events`.
    * Eventos: `user_registered`, `login_success`, `product_created`, `config_updated`, `contact_form_sent`, `tenant_created`, y más.
* **Superadministrador global:**
    * Creación de nuevos tenants (funerarias) con su propio admin.
    * Protegido por API Key (MVP) o por rol de superadmin en Keycloak (producción).

---

## Instrucciones de Instalación y Ejecución

### Requisitos previos

* Docker 24+ y Docker Compose v2
* Git
* 8 GB de RAM recomendados (mínimo 4 GB)
* Puertos disponibles: 27017, 5000, 4200, 8080, 9092, 8088

### 1. Clonar el repositorio

```bash
git clone [https://github.com/tu-usuario/funeraria-platform.git](https://github.com/tu-usuario/funeraria-platform.git)
cd funeraria-platform
```

### 2. Levantar todos los contenedores

```bash
docker-compose up -d
```

Esto iniciará 6 servicios:
* `funeraria_mongo` (MongoDB 7 en puerto 27017)
* `funeraria_backend` (Flask + Gunicorn en puerto 5000)
* `funeraria_frontend` (Angular + Nginx en puerto 4200)
* `funeraria_keycloak` (Keycloak en puerto 8080)
* `funeraria_kafka` (Apache Kafka en puerto 9092)
* `funeraria_kafka_ui` (Kafka UI en puerto 8088)

> **Nota:** Espera 2 minutos para que Keycloak termine de iniciar completamente.

### 3. Configurar Keycloak (Realm, Cliente y Roles)

```bash
bash keycloak/init-realm.sh
```

Este script crea automáticamente:
* **Realm:** `funeraria-realm`
* **Cliente:** `funeraria-client`
* **Roles:** `admin`, `operario`

Para verificar que Keycloak está funcionando, accede a `http://localhost:8080` con credenciales `admin` / `admin`.

### 4. Poblar datos de prueba (Seed)

```bash
docker exec -it funeraria_backend python seed.py
```

Esto crea:
* **Tenant 1:** Casa Funeraria La Eternidad (slug: `eternidad`)
* **Tenant 2:** Funeraria Ejemplo (slug: `ejemplo`)
* Admin para cada tenant.
* Productos de ejemplo (flores y ataúdes) para cada tenant.

### 5. Acceder al sistema

| Servicio | URL |
| :--- | :--- |
| **Frontend (Portal público)** | `http://localhost:4200` |
| **Frontend (Portal admin)** | `http://localhost:4200/admin` |
| **Backend API** | `http://localhost:5000` |
| **Keycloak Admin Console** | `http://localhost:8080` |
| **Kafka UI (monitoreo)** | `http://localhost:8088` |

---

## Guía paso a paso para probar el flujo completo

### 🔐 Fase 1: Autenticación (Login con Keycloak)

Login como admin de La Eternidad:

```bash
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@eternidad.com","password":"admin123","tenant_slug":"eternidad"}' \
  | python -m json.tool
```

Respuesta esperada:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ...",
  "user": {
    "id": "...",
    "email": "admin@eternidad.com",
    "role": "admin",
    "first_name": "Admin",
    "last_name": "Casa Funeraria La Eternidad"
  }
}
```

Guarda el token en una variable para usarlo en los siguientes pasos:

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@eternidad.com","password":"admin123","tenant_slug":"eternidad"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

**Verificar evento en Kafka UI:**
Accede a `http://localhost:8088` → Tópico `auth-events` → Deberías ver el mensaje `login_success`.

### 🎯 Fase 2: Operaciones de dominio (Productos)

Crear un producto (arreglo floral):

```bash
curl -s -X POST http://localhost:5000/api/admin/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Corona de Rosas","description":"Corona funeraria con rosas rojas","price":180000,"type":"flower"}' \
  | python -m json.tool
```

**Verificar evento en Kafka UI:**
Tópico `product-events` → Mensaje `product_created` con los datos del producto.

Listar productos del tenant:

```bash
curl -s http://localhost:5000/api/admin/products/ \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
```

### 🎨 Fase 3: Personalización del portal

Cambiar colores del tenant:

```bash
curl -s -X PUT http://localhost:5000/api/admin/config/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"primary_color":"#18222e","secondary_color":"#bf9f62"}' \
  | python -m json.tool
```

**Verificar evento en Kafka UI:**
Tópico `config-events` → Mensaje `config_updated`.

**Ver el portal público personalizado:**
Accede a `http://localhost:4200?tenant=eternidad` → Los colores y el logo se cargan dinámicamente.

### 🏢 Fase 4: Creación de un nuevo tenant (Superadmin)

```bash
curl -s -X POST http://localhost:5000/api/superadmin/tenants \
  -H "Content-Type: application/json" \
  -H "X-API-Key: superadmin-apikey-dev" \
  -d '{"name":"Funeraria Nueva","slug":"nueva","admin_email":"admin@nueva.com","admin_password":"pass123"}' \
  | python -m json.tool
```

**Verificar evento en Kafka UI:**
Tópico `tenant-events` → Mensaje `tenant_created`.

Ahora puedes acceder al nuevo portal en `http://localhost:4200?tenant=nueva` y hacer login con `admin@nueva.com` / `pass123`.

### 🛡️ Fase 5: Verificación de aislamiento multitenant

Intentar acceder a un producto de otro tenant:

```bash
# Token de admin de La Eternidad (tenant_id = A)
# Intentar acceder a un producto que pertenece a Funeraria Ejemplo (tenant_id = B)

curl -s http://localhost:5000/api/admin/products/ID_DE_PRODUCTO_DE_EJEMPLO \
  -H "Authorization: Bearer $TOKEN_ETERNIDAD" \
  | python -m json.tool
# Respuesta esperada: 404 Not Found
```

Intentar listar usuarios de otro tenant:

```bash
curl -s http://localhost:5000/api/admin/users/ \
  -H "Authorization: Bearer $TOKEN_ETERNIDAD" \
  | python -m json.tool
# Solo devuelve usuarios del tenant "eternidad"
```

---

## Estructura del Proyecto

```text
funeraria-platform/
│
├── backend/
│   ├── app.py                  # Factory create_app() con Blueprints, Keycloak y Kafka
│   ├── config.py               # Variables de entorno: JWT, Mongo, Keycloak, Kafka
│   ├── requirements.txt        # Dependencias Python (Flask, PyMongo, confluent-kafka, etc.)
│   ├── Dockerfile              # Imagen Python + Gunicorn
│   ├── seed.py                 # Datos iniciales: tenants, admins, productos de ejemplo
│   ├── utils/
│   │   ├── db.py               # Conexión singleton a MongoDB
│   │   └── file_upload.py      # Almacenamiento de logos e imágenes por tenant
│   ├── middleware/
│   │   ├── tenant.py           # extract_tenant: valida token Keycloak → g.tenant_id
│   │   └── auth.py             # role_required + jwt_required personalizados
│   └── modules/
│       ├── auth/               # Registro, login, logout, verify (Keycloak)
│       │   ├── routes.py
│       │   ├── services.py
│       │   └── keycloak_client.py
│       ├── public/             # Endpoints públicos: tenant, catálogo, contacto
│       │   ├── routes.py
│       │   └── services.py
│       ├── admin/              # Panel de administración: productos, configuración, usuarios
│       │   ├── catalog_routes.py
│       │   ├── config_routes.py
│       │   ├── user_routes.py
│       │   └── services.py
│       ├── superadmin/         # Gestión global de tenants
│       │   └── routes.py
│       └── kafka/              # Productor de eventos de dominio
│           └── producer.py
│
├── frontend/                   # Aplicación Angular 17
│   ├── angular.json
│   ├── Dockerfile              # Build Angular + Nginx
│   ├── nginx.conf
│   └── src/
│       ├── styles.css          # CSS custom properties para temas dinámicos
│       ├── environments/
│       └── app/
│           ├── core/
│           │   ├── services/   # AuthService, TenantService, CatalogService
│           │   ├── guards/     # AuthGuard
│           │   └── interceptors/ # TokenInterceptor, TenantInterceptor
│           └── modules/
│               ├── public/     # Home, Catalog, Contact, About
│               ├── admin/      # Dashboard, Products, Users, Config
│               └── auth/       # Login, Register
│
├── keycloak/
│   └── init-realm.sh           # Script para crear realm, cliente y roles en Keycloak
│
├── docker-compose.yml          # Servicios: mongodb, backend, frontend, keycloak, kafka, kafka-ui
└── README.md
```

---

## Comandos de verificación rápida

```bash
# Health check del backend
curl http://localhost:5000/api/public/tenant?slug=eternidad

# Login y obtener token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@eternidad.com","password":"admin123","tenant_slug":"eternidad"}'

# Crear producto con token
curl -X POST http://localhost:5000/api/admin/products/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test","price":100,"type":"flower"}'

# Ver eventos en Kafka UI
# Abrir http://localhost:8088 y revisar los tópicos
```

---

## Credenciales de prueba

| Tenant | Slug | Email | Contraseña | Rol |
| :--- | :--- | :--- | :--- | :--- |
| Casa Funeraria La Eternidad | `eternidad` | `admin@eternidad.com` | `admin123` | `admin` |
| Funeraria Ejemplo | `ejemplo` | `admin@ejemplo.com` | `admin123` | `admin` |

* **Superadmin API Key:** `superadmin-apikey-dev`
* **Keycloak Admin:** `admin` / `admin`

---

## Notas importantes

* La primera vez que se levanta Keycloak, es necesario ejecutar `keycloak/init-realm.sh` para crear el realm, cliente y roles. Si no se ejecuta, el login fallará con error `401`.
* El orden de arranque importa: levanta los contenedores, espera 2 minutos, ejecuta el script de Keycloak, y luego el seed.
* Los tenants se identifican por slug. En desarrollo local, el frontend captura el slug vía query param (`?tenant=eternidad`). En producción se usará subdominio (`eternidad.plataforma.com`).
* Las contraseñas en MongoDB son almacenadas con bcrypt como respaldo, pero la autenticación se delega completamente en Keycloak.
* Los eventos de Kafka se publican de forma asíncrona. Si el broker no está disponible, el sistema funciona sin eventos pero los logs registrarán advertencias.
* El panel de superadmin está protegido por API Key (`X-API-Key: superadmin-apikey-dev`). En producción se integrará con un rol de Keycloak.
* Para desarrollo local sin Docker, ejecuta `python app.py` en `backend/` y `ng serve` en `frontend/`, con MongoDB corriendo en `localhost:27017`.

---

## Solución de problemas comunes

| Problema | Causa probable | Solución |
| :--- | :--- | :--- |
| **401 Unauthorized en login** | Keycloak no inicializado | Ejecuta `bash keycloak/init-realm.sh` |
| **Connection refused en backend** | MongoDB no iniciado | Espera 30 segundos y reintenta |
| **Kafka UI vacío** | Eventos no publicados | Realiza alguna operación (login o crear producto) |
| **403 Forbidden en ruta admin** | Token inválido o expirado | Vuelve a hacer login |
| **404 Not Found al acceder a producto**| Producto de otro tenant o no existe | Verifica que usas el token del tenant correcto |
| **Build Angular falla** | Dependencias desactualizadas | Ejecuta `npm ci` dentro del contenedor frontend |

---

## Próximas características

* Integración con pasarela de pagos (para membresías).
* Dominios personalizados por tenant.
* Dashboard con estadísticas de visitas y contactos por funeraria.
* Exportación de catálogos a PDF.
* Notificaciones por correo electrónico a administradores (desde Kafka Consumer).
* Plantillas de diseño adicionales para el portal público.
* Tests unitarios y de integración (pytest + Jasmine/Karma).
* Migración a Kubernetes para alta disponibilidad.

---

## Desarrolladores

* **CRISTIAN CAMILO GALINDO SUAREZ** — Backend e Infraestructura
* **ANGEL SAMUEL GONZALEZ SAMBRANO** — Frontend y Despliegue

## Licencia

MIT © 2026 - Proyecto académico con proyección empresarial
