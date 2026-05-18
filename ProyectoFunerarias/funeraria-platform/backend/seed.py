"""
Script para poblar datos iniciales en MongoDB y crear usuarios en Keycloak.
Ejecutar después de levantar los contenedores y configurar Keycloak:
  docker exec -it funeraria_backend python seed.py
"""
from pymongo import MongoClient
from datetime import datetime
import requests
import bcrypt
import time

MONGO_URI = "mongodb://mongodb:27017/funeraria_db"
KEYCLOAK_BASE = "http://keycloak:8080"
REALM = "funeraria-realm"
CLIENT_ID = "funeraria-client"
CLIENT_SECRET = "funeraria-client-secret"

client = MongoClient(MONGO_URI)
db = client.get_default_database()

# ------------------------------------------------------------
# Funciones auxiliares para Keycloak
# ------------------------------------------------------------
def get_keycloak_admin_token():
    """Obtiene un token de administrador en el master realm."""
    url = f"{KEYCLOAK_BASE}/realms/master/protocol/openid-connect/token"
    payload = {
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password"
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()["access_token"]

def create_keycloak_user(admin_token, email, password, role, first_name="", last_name=""):
    """Crea un usuario en el realm funeraria-realm y le asigna el rol indicado."""
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 1. Crear usuario
    username = email
    user_payload = {
        "username": username,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
        "enabled": True,
        "emailVerified": True
    }
    resp = requests.post(
        f"{KEYCLOAK_BASE}/admin/realms/{REALM}/users",
        json=user_payload,
        headers=headers
    )
    if resp.status_code == 201:
        user_id = resp.headers["Location"].split("/")[-1]
    elif resp.status_code == 409 or "User exists" in resp.text:
        print(f"Usuario {email} ya existe en Keycloak. Eliminando versión anterior para recrearlo limpio...")
        get_resp = requests.get(
            f"{KEYCLOAK_BASE}/admin/realms/{REALM}/users?username={username}",
            headers=headers
        )
        if get_resp.status_code == 200 and len(get_resp.json()) > 0:
            old_user_id = get_resp.json()[0]["id"]
            del_resp = requests.delete(
                f"{KEYCLOAK_BASE}/admin/realms/{REALM}/users/{old_user_id}",
                headers=headers
            )
            if del_resp.status_code not in [200, 204]:
                print(f"ERROR al eliminar usuario antiguo {email}: {del_resp.status_code} {del_resp.text}")
                return None
            
            # Recrear el usuario limpio
            resp = requests.post(
                f"{KEYCLOAK_BASE}/admin/realms/{REALM}/users",
                json=user_payload,
                headers=headers
            )
            if resp.status_code == 201:
                user_id = resp.headers["Location"].split("/")[-1]
            else:
                print(f"ERROR al recrear usuario {email}: {resp.status_code} {resp.text}")
                return None
        else:
            print(f"ERROR al obtener usuario existente {email}: {get_resp.status_code}")
            return None
    else:
        print(f"ERROR al crear usuario {email}: {resp.status_code} {resp.text}")
        return None

    # 2. Obtener representación del rol
    role_resp = requests.get(
        f"{KEYCLOAK_BASE}/admin/realms/{REALM}/roles/{role}",
        headers=headers
    )
    if role_resp.status_code != 200:
        print(f"ERROR al obtener rol {role}: {role_resp.status_code} {role_resp.text}")
        return None

    role_data = role_resp.json()

    # 3. Asignar rol al usuario
    assign_url = f"{KEYCLOAK_BASE}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm"
    assign_resp = requests.post(assign_url, json=[role_data], headers=headers)
    if assign_resp.status_code == 204:
        print(f"Usuario {email} creado con rol {role} (ID: {user_id})")
        return user_id
    else:
        print(f"ERROR al asignar rol a {email}: {assign_resp.status_code} {assign_resp.text}")
        return None

# ------------------------------------------------------------
# Limpiar colecciones existentes
# ------------------------------------------------------------
db.tenants.delete_many({})
db.users.delete_many({})
db.products.delete_many({})
db.contacts.delete_many({})

# ------------------------------------------------------------
# Crear tenants y usuarios en Keycloak + MongoDB
# ------------------------------------------------------------
admin_token = get_keycloak_admin_token()
print("Token de administrador de Keycloak obtenido.")

# ---- Tenant 1: La Eternidad ----
tenant1 = {
    "name": "Casa Funeraria La Eternidad",
    "slug": "eternidad",
    "logo_url": "/assets/logos/logoLaEternidad.png",
    "primary_color": "#18222e",
    "secondary_color": "#bf9f62",
    "accent_color": "#ccad52",
    "background_color": "#0d1117",
    "text_color": "#e0e3e8",
    "contact_email": "funerarialaeternidad@hotmail.com",
    "whatsapp_number": "573132569671",
    "bank_accounts": "Banco Ejemplo, Cuenta #123456",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result1 = db.tenants.insert_one(tenant1)
tenant1_id = result1.inserted_id

kc_id = create_keycloak_user(admin_token, "admin@eternidad.com", "admineternidad", "admin", "Rigoberto", "Murcia")
if kc_id:
    user1 = {
        "keycloak_id": kc_id,
        "email": "admin@eternidad.com",
        "password_hash": bcrypt.hashpw("admineternidad".encode(), bcrypt.gensalt()).decode(),
        "role": "admin",
        "tenant_id": tenant1_id,
        "first_name": "Rigoberto",
        "last_name": "Murcia",
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user1)
    print("Admin de Eternidad insertado en MongoDB.")

# ---- Tenant 2: Los Olivos ----
tenant2 = {
    "name": "Funeraria Los Olivos",
    "slug": "losolivos",
    "logo_url": "/assets/logos/logoLosOlivos.png",
    "primary_color": "#006338",
    "secondary_color": "#C6A152",
    "accent_color": "#D4AF37",
    "background_color": "#ffffff",
    "text_color": "#333333",
    "contact_email": "info@losolivos.com",
    "whatsapp_number": "573001234567",
    "bank_accounts": "Banco Prueba, Cuenta #654321",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result2 = db.tenants.insert_one(tenant2)
tenant2_id = result2.inserted_id

kc_id2 = create_keycloak_user(admin_token, "admin@losolivos.com", "adminolivos", "admin", "Admin", "Olivos")
if kc_id2:
    user2 = {
        "keycloak_id": kc_id2,
        "email": "admin@losolivos.com",
        "password_hash": bcrypt.hashpw("adminolivos".encode(), bcrypt.gensalt()).decode(),
        "role": "admin",
        "tenant_id": tenant2_id,
        "first_name": "Admin",
        "last_name": "Olivos",
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user2)
    print("Admin de Los Olivos insertado en MongoDB.")

# ---- Tenant 3: Funeraria Central ----
tenant3 = {
    "name": "Funeraria Central",
    "slug": "central",
    "logo_url": "/assets/logos/logoFuneCentral.jpg",
    "primary_color": "#3b3b3b",
    "secondary_color": "#c8b27f",
    "accent_color": "#c8b27f",
    "background_color": "#f2f2f2",
    "text_color": "#3b3b3b",
    "contact_email": "info@funerariacentral.com",
    "whatsapp_number": "573009876543",
    "bank_accounts": "Banco Nacional, Cuenta #789012",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result3 = db.tenants.insert_one(tenant3)
tenant3_id = result3.inserted_id

kc_id3 = create_keycloak_user(admin_token, "admin@central.com", "admincentral", "admin", "Admin", "Central")
if kc_id3:
    user3 = {
        "keycloak_id": kc_id3,
        "email": "admin@central.com",
        "password_hash": bcrypt.hashpw("admincentral".encode(), bcrypt.gensalt()).decode(),
        "role": "admin",
        "tenant_id": tenant3_id,
        "first_name": "Admin",
        "last_name": "Central",
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user3)
    print("Admin de Funeraria Central insertado en MongoDB.")


# ---- Productos de ejemplo ----
# Eternidad
db.products.insert_one({
    "tenant_id": tenant1_id,
    "type": "flower",
    "title": "Ramo de Rosas Rojas Premium",
    "description": "12 rosas rojas con follaje decorativo. Ideal para expresar amor y respeto.",
    "price": 150000,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})
db.products.insert_one({
    "tenant_id": tenant1_id,
    "type": "coffin",
    "title": "Ataúd Clásico en Madera de Cedro",
    "description": "Ataúd elaborado en madera de cedro con acabados en dorado.",
    "price": None,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})

# Los Olivos
db.products.insert_one({
    "tenant_id": tenant2_id,
    "type": "flower",
    "title": "Corona de Lirios Blancos",
    "description": "Corona funeraria con lirios blancos y verdes decorativos.",
    "price": 120000,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})
db.products.insert_one({
    "tenant_id": tenant2_id,
    "type": "coffin",
    "title": "Ataúd Modelo Contemporáneo",
    "description": "Ataúd moderno en color gris perla con interior acolchado.",
    "price": None,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})

# Funeraria Central
db.products.insert_one({
    "tenant_id": tenant3_id,
    "type": "flower",
    "title": "Arreglo Floral Elegante",
    "description": "Arreglo con claveles blancos y rosas en tonos pastel.",
    "price": 95000,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})
db.products.insert_one({
    "tenant_id": tenant3_id,
    "type": "coffin",
    "title": "Ataúd Tradicional en Caoba",
    "description": "Féretro clásico en madera de caoba con herrajes plateados.",
    "price": None,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
})

print("\n✅ Datos de prueba insertados correctamente.")
print("   - Tenant 1: 'eternidad' con admin admin@eternidad.com / admineternidad")
print("   - Tenant 2: 'losolivos' con admin admin@losolivos.com / adminolivos")
print("   - Tenant 3: 'central'   con admin admin@central.com / admincentral")
print("   - Productos de ejemplo creados para cada tenant.")

client.close()