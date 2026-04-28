from bson import ObjectId
from datetime import datetime
from utils.db import Database

class AdminService:
    @staticmethod
    def get_config(tenant_id):
        db = Database.get_db()
        return db.tenants.find_one({"_id": ObjectId(tenant_id)})

    @staticmethod
    def update_config(tenant_id, updates):
        db = Database.get_db()
        allowed_fields = ['primary_color', 'secondary_color', 'contact_email', 'whatsapp_number', 'bank_accounts']
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}
        if update_data:
            db.tenants.update_one({"_id": ObjectId(tenant_id)}, {"$set": update_data})
        return AdminService.get_config(tenant_id)

    @staticmethod
    def create_product(tenant_id, product_data):
        db = Database.get_db()
        product = {
            "tenant_id": ObjectId(tenant_id),
            "type": product_data.get('type', 'flower'),
            "title": product_data.get('title'),
            "description": product_data.get('description', ''),
            "price": product_data.get('price'),
            "image_url": product_data.get('image_url', ''),
            "is_visible": True,
            "created_at": datetime.utcnow()
        }
        result = db.products.insert_one(product)
        product['_id'] = result.inserted_id
        return product

    @staticmethod
    def update_product(product_id, tenant_id, updates):
        db = Database.get_db()
        allowed_fields = ['title', 'description', 'price', 'image_url', 'is_visible', 'type']
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}
        if update_data:
            db.products.update_one(
                {"_id": ObjectId(product_id), "tenant_id": ObjectId(tenant_id)},
                {"$set": update_data}
            )
        return db.products.find_one({"_id": ObjectId(product_id), "tenant_id": ObjectId(tenant_id)})

    @staticmethod
    def delete_product(product_id, tenant_id):
        db = Database.get_db()
        result = db.products.delete_one({"_id": ObjectId(product_id), "tenant_id": ObjectId(tenant_id)})
        return result.deleted_count > 0

    @staticmethod
    def list_products(tenant_id, product_type=None):
        db = Database.get_db()
        query = {"tenant_id": ObjectId(tenant_id)}
        if product_type:
            query["type"] = product_type
        return list(db.products.find(query))

    @staticmethod
    def list_users(tenant_id):
        db = Database.get_db()
        return list(db.users.find({"tenant_id": ObjectId(tenant_id)}))
