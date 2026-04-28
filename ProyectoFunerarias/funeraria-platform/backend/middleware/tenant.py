from flask import g, request, jsonify
from modules.auth.keycloak_client import get_keycloak_client
from utils.db import Database

def extract_tenant():
    """Extrae token de Keycloak, obtiene userinfo y guarda en g (para rutas autenticadas)"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        kc = get_keycloak_client()
        try:
            # Para validar el token localmente o consultar a Keycloak
            user_info = kc.verify_token(token)
            keycloak_id = user_info.get('sub')
            
            # Buscar el usuario en MongoDB
            db = Database.get_db()
            user = db.users.find_one({"keycloak_id": keycloak_id})
            
            if user:
                g.tenant_id = str(user.get('tenant_id'))
                g.user_id = str(user.get('_id'))
                g.role = user.get('role')
            else:
                # Si el usuario está en Keycloak pero no en MongoDB (ej. admin recién creado)
                # Opcional: manejar este caso si es necesario
                pass
        except Exception as e:
            # Token inválido o no existe, simplemente continuamos sin popular `g`
            # Las rutas protegidas lo validarán después
            pass
