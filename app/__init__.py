from flask import Flask
from app.src.routes import register_routes
from app.src import config
from datetime import timedelta

def create_app():
    """Tạo và cấu hình ứng dụng Flask."""
    app = Flask(__name__, 
                template_folder=config.TEMPLATE_FOLDER,
                static_folder=config.STATIC_FOLDER)
    
    # Cấu hình ứng dụng
    app.config.from_object(config)
    app.secret_key = config.SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=config.PERMANENT_SESSION_LIFETIME.seconds)
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    # Đăng ký các route
    register_routes(app)
    
    return app 