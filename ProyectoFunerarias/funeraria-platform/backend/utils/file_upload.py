import os
from werkzeug.utils import secure_filename
from config import Config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, tenant_id, subfolder=''):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        tenant_path = os.path.join(Config.UPLOAD_FOLDER, str(tenant_id), subfolder)
        os.makedirs(tenant_path, exist_ok=True)
        filepath = os.path.join(tenant_path, filename)
        file.save(filepath)
        return f'/uploads/{tenant_id}/{subfolder}/{filename}'
    return None
