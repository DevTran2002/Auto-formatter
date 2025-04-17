import os
import tempfile
from datetime import timedelta

# Cấu hình cơ bản
APP_NAME = "Document Formatter"
VERSION = "1.0.0"

# Cấu hình đường dẫn
UPLOAD_FOLDER = os.path.abspath('uploads')
TEMP_FOLDER = tempfile.gettempdir()

# Đảm bảo thư mục tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Cấu hình tệp
ALLOWED_EXTENSIONS = {'doc', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

# Cấu hình Flask
DEBUG = True
SECRET_KEY = os.urandom(24)
PERMANENT_SESSION_LIFETIME = timedelta(seconds=300)

# Cấu hình đường dẫn template và static
TEMPLATE_FOLDER = 'app/templates'
STATIC_FOLDER = 'app/static' 