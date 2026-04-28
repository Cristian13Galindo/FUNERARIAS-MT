from datetime import datetime
import bcrypt
from bson import ObjectId
from utils.db import Database

class AuthService:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def create_user(email, password, role, tenant_id, first_name='', last_name=''):
        db = Database.get_db()
        user = {
            "email": email,
            "password_hash": AuthService.hash_password(password),
            "role": role,
            "tenant_id": ObjectId(tenant_id) if isinstance(tenant_id, str) else tenant_id,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.utcnow()
        }
        result = db.users.insert_one(user)
        user['_id'] = result.inserted_id
        return user

    @staticmethod
    def find_by_email(email, tenant_id=None):
        db = Database.get_db()
        query = {"email": email}
        if tenant_id:
            query["tenant_id"] = ObjectId(tenant_id) if isinstance(tenant_id, str) else tenant_id
        return db.users.find_one(query)
