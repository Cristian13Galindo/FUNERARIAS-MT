from flask import Blueprint, request, jsonify, g
from middleware.auth import jwt_required, role_required
from modules.auth.services import AuthService
from modules.admin.services import AdminService
from modules.auth.keycloak_client import get_keycloak_client
from utils.db import Database
from bson import ObjectId
from datetime import datetime

admin_user_bp = Blueprint('admin_user', __name__)

@admin_user_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    users = AdminService.list_users(g.tenant_id)
    for u in users:
        u['_id'] = str(u['_id'])
        u['tenant_id'] = str(u['tenant_id'])
        u.pop('password_hash', None)
    return jsonify(users), 200

@admin_user_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'operario')

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    db = Database.get_db()
    if db.users.find_one({"email": email, "tenant_id": ObjectId(g.tenant_id)}):
        return jsonify({"msg": "El usuario ya existe"}), 409

    kc = get_keycloak_client()
    try:
        kc_id = kc.create_user(email, password, data.get('first_name', ''), data.get('last_name', ''), role)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    user = {
        "email": email,
        "keycloak_id": kc_id,
        "tenant_id": ObjectId(g.tenant_id),
        "role": role,
        "first_name": data.get('first_name', ''),
        "last_name": data.get('last_name', ''),
        "is_active": True
    }
    result = db.users.insert_one(user)

    return jsonify({"msg": "Usuario creado", "user_id": str(result.inserted_id)}), 201


@admin_user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    """Edita nombre, apellido y/o rol de un operario del mismo tenant."""
    data = request.get_json()
    db = Database.get_db()

    # Verificar que el usuario pertenezca al tenant del admin autenticado
    user = db.users.find_one({
        "_id": ObjectId(user_id),
        "tenant_id": ObjectId(g.tenant_id)
    })
    if not user:
        return jsonify({"msg": "Usuario no encontrado o no pertenece a este tenant"}), 404

    allowed_fields = ['first_name', 'last_name', 'role']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"msg": "No se enviaron campos válidos para actualizar"}), 400

    update_data['updated_at'] = datetime.utcnow()
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    updated = db.users.find_one({"_id": ObjectId(user_id)})
    updated['_id'] = str(updated['_id'])
    updated['tenant_id'] = str(updated['tenant_id'])
    updated.pop('password_hash', None)

    return jsonify({"msg": "Usuario actualizado", "user": updated}), 200


@admin_user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def deactivate_user(user_id):
    """Soft delete: desactiva un operario del mismo tenant (is_active = False)."""
    db = Database.get_db()

    # Verificar que el usuario pertenezca al tenant del admin autenticado
    user = db.users.find_one({
        "_id": ObjectId(user_id),
        "tenant_id": ObjectId(g.tenant_id)
    })
    if not user:
        return jsonify({"msg": "Usuario no encontrado o no pertenece a este tenant"}), 404

    # Evitar que el admin se desactive a sí mismo
    if str(user['_id']) == g.user_id:
        return jsonify({"msg": "No puedes desactivar tu propia cuenta"}), 400

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False, "deactivated_at": datetime.utcnow()}}
    )
    return jsonify({"msg": f"Usuario {user.get('email')} desactivado correctamente"}), 200
