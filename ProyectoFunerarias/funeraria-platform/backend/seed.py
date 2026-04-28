"""
Script para poblar datos iniciales en MongoDB.
Ejecutar después de levantar los contenedores:
  docker exec -it funeraria_backend python seed.py
"""
from pymongo import MongoClient
from datetime import datetime
import bcrypt

MONGO_URI = "mongodb://mongodb:27017/funeraria_db"
client = MongoClient(MONGO_URI)
db = client.get_default_database()

# Limpiar colecciones existentes (opcional, comentar si no se desea)
db.tenants.delete_many({})
db.users.delete_many({})
db.products.delete_many({})
db.contacts.delete_many({})

# Crear Tenant 1: La Eternidad
tenant1 = {
    "name": "Casa Funeraria La Eternidad",
    "slug": "eternidad",
    "logo_url": None,
    "primary_color": "#18222e",
    "secondary_color": "#bf9f62",
    "contact_email": "funerarialaeternidad@hotmail.com",
    "whatsapp_number": "573132569671",
    "bank_accounts": "Banco Ejemplo, Cuenta #123456",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result1 = db.tenants.insert_one(tenant1)
tenant1_id = result1.inserted_id

# Crear Tenant 2: Funeraria Ejemplo
tenant2 = {
    "name": "Funeraria Ejemplo",
    "slug": "ejemplo",
    "logo_url": None,
    "primary_color": "#1a1a1a",
    "secondary_color": "#d4af37",
    "contact_email": "info@ejemplo.com",
    "whatsapp_number": "573001234567",
    "bank_accounts": "Banco Prueba, Cuenta #654321",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result2 = db.tenants.insert_one(tenant2)
tenant2_id = result2.inserted_id

# Crear usuarios admin para cada tenant
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

admin1 = {
    "email": "admin@eternidad.com",
    "password_hash": hash_password("admin123"),
    "role": "admin",
    "tenant_id": tenant1_id,
    "first_name": "Rigoberto",
    "last_name": "Murcia",
    "created_at": datetime.utcnow()
}
db.users.insert_one(admin1)

admin2 = {
    "email": "admin@ejemplo.com",
    "password_hash": hash_password("admin123"),
    "role": "admin",
    "tenant_id": tenant2_id,
    "first_name": "Admin",
    "last_name": "Ejemplo",
    "created_at": datetime.utcnow()
}
db.users.insert_one(admin2)

# Crear algunos productos de ejemplo para cada tenant
product1_1 = {
    "tenant_id": tenant1_id,
    "type": "flower",
    "title": "Ramo de Rosas Rojas Premium",
    "description": "12 rosas rojas con follaje decorativo. Ideal para expresar amor y respeto.",
    "price": 150000,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
}
db.products.insert_one(product1_1)

product1_2 = {
    "tenant_id": tenant1_id,
    "type": "coffin",
    "title": "Ataúd Clásico en Madera de Cedro",
    "description": "Ataúd elaborado en madera de cedro con acabados en dorado. Diseño sobrio y elegante.",
    "price": None,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
}
db.products.insert_one(product1_2)

product2_1 = {
    "tenant_id": tenant2_id,
    "type": "flower",
    "title": "Corona de Lirios Blancos",
    "description": "Corona funeraria con lirios blancos y verdes decorativos.",
    "price": 120000,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
}
db.products.insert_one(product2_1)

product2_2 = {
    "tenant_id": tenant2_id,
    "type": "coffin",
    "title": "Ataúd Modelo Contemporáneo",
    "description": "Ataúd moderno en color gris perla con interior acolchado.",
    "price": None,
    "image_url": None,
    "is_visible": True,
    "created_at": datetime.utcnow()
}
db.products.insert_one(product2_2)

print("✅ Datos de prueba insertados correctamente.")
print(f"   - Tenant 1: 'eternidad' con admin admin@eternidad.com / admin123")
print(f"   - Tenant 2: 'ejemplo' con admin admin@ejemplo.com / admin123")
print(f"   - Productos de ejemplo creados para cada tenant.")

client.close()
