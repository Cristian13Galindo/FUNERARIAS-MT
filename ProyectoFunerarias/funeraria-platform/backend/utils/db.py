from pymongo import MongoClient
from config import Config

class Database:
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(Config.MONGO_URI)
            cls._db = cls._client.get_default_database()
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
