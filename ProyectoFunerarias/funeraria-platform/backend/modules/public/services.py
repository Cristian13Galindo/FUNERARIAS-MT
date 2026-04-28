from bson import ObjectId
from utils.db import Database

class PublicService:
    @staticmethod
    def get_tenant_by_slug(slug):
        db = Database.get_db()
        return db.tenants.find_one({"slug": slug, "is_active": True})

    @staticmethod
    def get_products(tenant_id, product_type=None):
        db = Database.get_db()
        query = {"tenant_id": ObjectId(tenant_id), "is_visible": True}
        if product_type:
            query["type"] = product_type
        return list(db.products.find(query))
