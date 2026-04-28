from flask import Blueprint, request, jsonify, g
from middleware.auth import jwt_required, role_required
from modules.admin.services import AdminService
from modules.kafka.producer import get_producer
from bson import ObjectId

admin_catalog_bp = Blueprint('admin_catalog', __name__)

@admin_catalog_bp.route('/', methods=['GET'])
@jwt_required()
def list_products():
    product_type = request.args.get('type')
    products = AdminService.list_products(g.tenant_id, product_type)
    for p in products:
        p['_id'] = str(p['_id'])
        p['tenant_id'] = str(p['tenant_id'])
    return jsonify(products), 200

@admin_catalog_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    product = AdminService.create_product(g.tenant_id, data)
    product['_id'] = str(product['_id'])
    product['tenant_id'] = str(product['tenant_id'])
    
    producer = get_producer()
    if producer:
        producer.publish_event('product-events', 'product_created', {"product_id": product['_id'], "tenant_id": g.tenant_id})
        
    return jsonify(product), 201

@admin_catalog_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    data = request.get_json()
    # Solo admin puede modificar precio
    if 'price' in data and g.role != 'admin':
        return jsonify({"msg": "Solo el administrador puede modificar precios"}), 403
    
    product = AdminService.update_product(product_id, g.tenant_id, data)
    if not product:
        return jsonify({"msg": "Producto no encontrado"}), 404
    product['_id'] = str(product['_id'])
    product['tenant_id'] = str(product['tenant_id'])
    
    producer = get_producer()
    if producer:
        producer.publish_event('product-events', 'product_updated', {"product_id": product['_id'], "tenant_id": g.tenant_id})
        
    return jsonify(product), 200

@admin_catalog_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    if AdminService.delete_product(product_id, g.tenant_id):
        producer = get_producer()
        if producer:
            producer.publish_event('product-events', 'product_deleted', {"product_id": product_id, "tenant_id": g.tenant_id})
        return jsonify({"msg": "Producto eliminado"}), 200
    return jsonify({"msg": "Producto no encontrado"}), 404
