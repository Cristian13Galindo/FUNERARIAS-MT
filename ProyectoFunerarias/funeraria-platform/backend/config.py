import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/funeraria_db')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supersecretkey')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    SUPERADMIN_API_KEY = os.getenv('SUPERADMIN_API_KEY', 'superadmin-apikey-dev')

    # Keycloak Config
    KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'http://keycloak:8080')
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'funeraria-realm')
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'funeraria-client')
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '')

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
