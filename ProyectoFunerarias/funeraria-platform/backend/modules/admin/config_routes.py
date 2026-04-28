from flask import Blueprint, request, jsonify, g
from middleware.auth import jwt_required, role_required
from modules.admin.services import AdminService
from modules.kafka.producer import get_producer
from utils.db import Database
from utils.file_upload import save_uploaded_file
from bson import ObjectId

admin_config_bp = Blueprint('admin_config', __name__)

@admin_config_bp.route('/', methods=['GET'])
@jwt_required()
def get_config():
    config = AdminService.get_config(g.tenant_id)
    if not config:
        return jsonify({"msg": "Configuración no encontrada"}), 404
    return jsonify({
        "id": str(config['_id']),
        "name": config['name'],
        "logo_url": config.get('logo_url'),
        "primary_color": config.get('primary_color'),
        "secondary_color": config.get('secondary_color'),
        "contact_email": config.get('contact_email'),
        "whatsapp_number": config.get('whatsapp_number'),
        "bank_accounts": config.get('bank_accounts')
    }), 200


@admin_config_bp.route('/', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_config():
    data = request.get_json()
    config = AdminService.update_config(g.tenant_id, data)
    
    producer = get_producer()
    if producer:
        producer.publish_event('config-events', 'config_updated', {"tenant_id": g.tenant_id})
        
    return jsonify({
        "msg": "Configuración actualizada",
        "config": {
            "primary_color": config.get('primary_color'),
            "secondary_color": config.get('secondary_color'),
            "contact_email": config.get('contact_email'),
            "whatsapp_number": config.get('whatsapp_number'),
        }
    }), 200


@admin_config_bp.route('/logo', methods=['POST'])
@jwt_required()
@role_required('admin')
def upload_logo():
    """
    Recibe un archivo en multipart/form-data con el campo 'image'.
    Guarda la imagen en UPLOAD_FOLDER/<tenant_id>/logo/ y actualiza
    el campo logo_url del tenant en MongoDB.
    """
    if 'image' not in request.files:
        return jsonify({"msg": "No se envió ningún archivo con el campo 'image'"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"msg": "El archivo no tiene nombre"}), 400

    logo_url = save_uploaded_file(file, g.tenant_id, subfolder='logo')
    if not logo_url:
        return jsonify({"msg": "Formato de archivo no permitido. Use png, jpg, jpeg o gif."}), 400

    # Actualizar logo_url en el tenant
    db = Database.get_db()
    db.tenants.update_one(
        {"_id": ObjectId(g.tenant_id)},
        {"$set": {"logo_url": logo_url}}
    )
    
    producer = get_producer()
    if producer:
        producer.publish_event('config-events', 'logo_uploaded', {"tenant_id": g.tenant_id, "logo_url": logo_url})

    return jsonify({
        "msg": "Logo actualizado correctamente",
        "logo_url": logo_url
    }), 200
