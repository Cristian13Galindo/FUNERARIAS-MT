from flask import Blueprint, request, jsonify
from config import Config
from modules.auth.keycloak_client import get_keycloak_client
from modules.kafka.producer import get_producer
from utils.db import Database
from datetime import datetime
from bson import ObjectId

superadmin_bp = Blueprint('superadmin', __name__)

def verify_superadmin():
    api_key = request.headers.get('X-API-Key')
    return api_key == Config.SUPERADMIN_API_KEY

@superadmin_bp.before_request
def check_superadmin():
    if not verify_superadmin():
        return jsonify({"msg": "Acceso denegado. API Key inválida."}), 403

@superadmin_bp.route('/tenants', methods=['POST'])
def create_tenant():
    data = request.get_json()
    name = data.get('name')
    slug = data.get('slug')
    admin_email = data.get('admin_email')
    admin_password = data.get('admin_password')

    if not all([name, slug, admin_email, admin_password]):
        return jsonify({"msg": "Faltan campos obligatorios: name, slug, admin_email, admin_password"}), 400

    db = Database.get_db()
    
    # Verificar slug único
    if db.tenants.find_one({"slug": slug}):
        return jsonify({"msg": "Ya existe una funeraria con ese slug"}), 409

    # Crear tenant
    tenant = {
        "name": name,
        "slug": slug,
        "logo_url": None,
        "primary_color": "#1a1a1a",
        "secondary_color": "#bf9f62",
        "contact_email": admin_email,
        "whatsapp_number": "",
        "bank_accounts": "",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    result = db.tenants.insert_one(tenant)
    tenant_id = result.inserted_id

    # Crear usuario admin en Keycloak
    kc = get_keycloak_client()
    try:
        kc_id = kc.create_user(admin_email, admin_password, "Admin", name, "admin")
    except Exception as e:
        # Rollback tenant si falla Keycloak
        db.tenants.delete_one({"_id": tenant_id})
        return jsonify({"msg": str(e)}), 400

    # Crear usuario admin en la DB local
    admin_user = {
        "email": admin_email,
        "keycloak_id": kc_id,
        "tenant_id": tenant_id,
        "role": "admin",
        "first_name": "Admin",
        "last_name": name,
        "is_active": True
    }
    db.users.insert_one(admin_user)
    
    producer = get_producer()
    if producer:
        producer.publish_event('tenant-events', 'tenant_created', {"tenant_id": str(tenant_id), "slug": slug})

    return jsonify({
        "msg": "Funeraria creada exitosamente",
        "tenant_id": str(tenant_id),
        "slug": slug,
        "admin_user_id": str(admin_user['_id'])
    }), 201

@superadmin_bp.route('/tenants', methods=['GET'])
def list_tenants():
    db = Database.get_db()
    tenants = list(db.tenants.find())
    for t in tenants:
        t['_id'] = str(t['_id'])
    return jsonify(tenants), 200

@superadmin_bp.route('/tenants/<tenant_id>/toggle', methods=['PATCH'])
def toggle_tenant(tenant_id):
    db = Database.get_db()
    tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
    if not tenant:
        return jsonify({"msg": "Funeraria no encontrada"}), 404
    new_status = not tenant.get('is_active', True)
    db.tenants.update_one({"_id": ObjectId(tenant_id)}, {"$set": {"is_active": new_status}})
    return jsonify({"msg": f"Estado actualizado a {'activo' if new_status else 'inactivo'}", "is_active": new_status}), 200
