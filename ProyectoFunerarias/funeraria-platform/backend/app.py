from flask import Flask
from flask_cors import CORS
from config import Config
from middleware.tenant import extract_tenant

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Extensiones
    CORS(app)
    
    # Inicializar Keycloak y Kafka
    from modules.auth.keycloak_client import init_keycloak
    init_keycloak(app)
    
    import modules.kafka.producer as kafka_producer
    kafka_producer.producer_instance = kafka_producer.KafkaEventProducer(app.config['KAFKA_BOOTSTRAP_SERVERS'])
    
    # Middleware de tenant se ejecuta antes de cada request
    app.before_request(extract_tenant)
    
    # Registrar Blueprints
    from modules.auth.routes import auth_bp
    from modules.public.routes import public_bp
    from modules.admin.config_routes import admin_config_bp
    from modules.admin.catalog_routes import admin_catalog_bp
    from modules.admin.user_routes import admin_user_bp
    from modules.superadmin.routes import superadmin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    app.register_blueprint(admin_config_bp, url_prefix='/api/admin/config')
    app.register_blueprint(admin_catalog_bp, url_prefix='/api/admin/products')
    app.register_blueprint(admin_user_bp, url_prefix='/api/admin/users')
    app.register_blueprint(superadmin_bp, url_prefix='/api/superadmin')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
