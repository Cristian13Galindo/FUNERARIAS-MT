from flask import Blueprint, request, jsonify, g
from middleware.auth import jwt_required
from modules.auth.keycloak_client import get_keycloak_client
from modules.kafka.producer import get_producer
from utils.db import Database
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    tenant_slug = data.get('tenant_slug')
    role = data.get('role', 'operario')

    if not email or not password or not tenant_slug:
        return jsonify({"msg": "Email, contraseña y slug son obligatorios"}), 400

    db = Database.get_db()
    tenant = db.tenants.find_one({"slug": tenant_slug})
    if not tenant:
        return jsonify({"msg": "Funeraria no encontrada"}), 404

    kc = get_keycloak_client()
    try:
        kc_id = kc.create_user(email, password, data.get('first_name', ''), data.get('last_name', ''), role)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    # Guardar en MongoDB
    user = {
        "email": email,
        "keycloak_id": kc_id,
        "tenant_id": tenant['_id'],
        "role": role,
        "first_name": data.get('first_name', ''),
        "last_name": data.get('last_name', ''),
        "is_active": True
    }
    db.users.insert_one(user)

    producer = get_producer()
    if producer:
        producer.publish_event('auth-events', 'user_registered', {"email": email, "tenant_id": str(tenant['_id'])})

    return jsonify({"msg": "Usuario registrado exitosamente"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    tenant_slug = data.get('tenant_slug')  # ahora es opcional

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    db = Database.get_db()

    # Autenticar contra Keycloak primero
    kc = get_keycloak_client()
    try:
        tokens = kc.login(email, password)
    except Exception as e:
        return jsonify({"msg": str(e)}), 401

    # Obtener el keycloak_id para validar
    user_info = kc.verify_token(tokens['access_token'])
    keycloak_id = user_info.get('sub')

    if tenant_slug:
        # Flujo original: buscar por email + tenant
        tenant = db.tenants.find_one({"slug": tenant_slug})
        if not tenant:
            return jsonify({"msg": "Funeraria no encontrada"}), 404
        user = db.users.find_one({"email": email, "tenant_id": tenant['_id']})
        if not user:
            user_any = db.users.find_one({"email": email})
            if user_any:
                return jsonify({"msg": "Usuario no autorizado para esta funeraria"}), 403
            else:
                return jsonify({"msg": "Usuario no encontrado en la base de datos"}), 404
    else:
        # Flujo nuevo: buscar solo por email y derivar tenant automáticamente
        user = db.users.find_one({"email": email})
        if not user:
            return jsonify({"msg": "Usuario no encontrado en la base de datos"}), 404
        tenant = db.tenants.find_one({"_id": user['tenant_id']})
        if not tenant:
            return jsonify({"msg": "Funeraria asociada no encontrada"}), 404
        tenant_slug = tenant['slug']

    # Auto-heal the keycloak_id if it's different or missing
    if user.get("keycloak_id") != keycloak_id:
        db.users.update_one({"_id": user['_id']}, {"$set": {"keycloak_id": keycloak_id}})


    producer = get_producer()
    if producer:
        producer.publish_event('auth-events', 'login_success', {"user_id": str(user['_id']), "tenant_id": str(tenant['_id'])})

    return jsonify({
        "access_token": tokens['access_token'],
        "refresh_token": tokens.get('refresh_token'),
        "tenant_slug": tenant_slug,
        "user": {
            "id": str(user['_id']),
            "email": user['email'],
            "role": user['role'],
            "first_name": user.get('first_name', ''),
            "last_name": user.get('last_name', '')
        }
    }), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    
    kc = get_keycloak_client()
    try:
        user_info = kc.verify_token(token)
    except Exception as e:
        return jsonify({"msg": str(e)}), 401

    db = Database.get_db()
    user = db.users.find_one({"keycloak_id": user_info.get('sub')})
    if not user:
        return jsonify({"msg": "Usuario no encontrado en la DB local"}), 404

    return jsonify({
        "valid": True,
        "user_id": str(user['_id']),
        "email": user['email'],
        "role": user['role'],
        "tenant_id": str(user['tenant_id'])
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token')
    
    if refresh_token:
        kc = get_keycloak_client()
        try:
            kc.logout(refresh_token)
        except Exception as e:
            pass
            
    producer = get_producer()
    if producer and hasattr(g, 'user_id'):
        producer.publish_event('auth-events', 'logout', {"user_id": g.user_id, "tenant_id": getattr(g, 'tenant_id', None)})

    return jsonify({"msg": "Sesión cerrada exitosamente"}), 200
