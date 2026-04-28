from flask import Blueprint, request, jsonify
from bson import ObjectId
from modules.public.services import PublicService
from modules.kafka.producer import get_producer
from utils.db import Database
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/tenant', methods=['GET'])
def get_tenant_info():
    slug = request.args.get('slug')
    if not slug:
        return jsonify({"msg": "Slug del tenant es requerido"}), 400
    
    tenant = PublicService.get_tenant_by_slug(slug)
    if not tenant:
        return jsonify({"msg": "Funeraria no encontrada"}), 404
    
    return jsonify({
        "id": str(tenant['_id']),
        "name": tenant['name'],
        "logo_url": tenant.get('logo_url'),
        "primary_color": tenant.get('primary_color', '#000000'),
        "secondary_color": tenant.get('secondary_color', '#ffffff'),
        "contact_email": tenant.get('contact_email'),
        "whatsapp_number": tenant.get('whatsapp_number'),
        "bank_accounts": tenant.get('bank_accounts')
    }), 200

@public_bp.route('/catalog', methods=['GET'])
def get_catalog():
    slug = request.args.get('tenant_slug')
    if not slug:
        return jsonify({"msg": "Slug del tenant es requerido"}), 400
    
    tenant = PublicService.get_tenant_by_slug(slug)
    if not tenant:
        return jsonify({"msg": "Funeraria no encontrada"}), 404
    
    product_type = request.args.get('type')  # 'flower' o 'coffin'
    products = PublicService.get_products(tenant['_id'], product_type)
    
    # Convertir ObjectId a string
    for p in products:
        p['_id'] = str(p['_id'])
        p['tenant_id'] = str(p['tenant_id'])
    
    return jsonify(products), 200

@public_bp.route('/contact', methods=['POST'])
def send_contact():
    data = request.get_json()
    slug = data.get('tenant_slug')
    if not slug:
        return jsonify({"msg": "Slug del tenant es requerido"}), 400
    
    tenant = PublicService.get_tenant_by_slug(slug)
    if not tenant:
        return jsonify({"msg": "Funeraria no encontrada"}), 404
    
    db = Database.get_db()
    message = {
        "tenant_id": tenant['_id'],
        "name": data.get('name', ''),
        "email": data.get('email', ''),
        "phone": data.get('phone', ''),
        "message": data.get('message', ''),
        "created_at": datetime.utcnow()
    }
    result = db.contacts.insert_one(message)
    
    producer = get_producer()
    if producer:
        producer.publish_event('contact-events', 'contact_form_sent', {"contact_id": str(result.inserted_id), "tenant_id": str(tenant['_id'])})
    
    # En producción, aquí se enviaría el correo real
    return jsonify({"msg": "Mensaje enviado correctamente", "id": str(result.inserted_id)}), 201
