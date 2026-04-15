import os

class Config:
    SECRET_KEY = 'pegasus-computer-store-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pegasus.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session配置
    SESSION_COOKIE_NAME = 'pegasus_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 分页配置
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10