import os
import time
import logging
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app

logger = logging.getLogger(__name__)

def allowed_file(filename):
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_and_save_image(file, prefix="upload"):
    """
    이미지를 최적화하여 저장하고 URL을 반환합니다.
    """
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        raise ValueError("허용되지 않는 파일 형식입니다.")

    UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    try:
        original_filename, _ = os.path.splitext(file.filename)
        timestamp = int(time.time())
        filename = secure_filename(f"{prefix}_{timestamp}_{original_filename}.jpg")
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        image = Image.open(file.stream)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        max_size = current_app.config.get('MAX_IMAGE_SIZE', (1920, 1920))
        image.thumbnail(max_size)
        
        quality = current_app.config.get('IMAGE_QUALITY', 85)
        image.save(filepath, 'JPEG', quality=quality)
        
        return f"/uploads/{filename}"
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise RuntimeError(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")

def delete_image_file(image_url):
    """
    이미지 파일이 존재하면 삭제합니다.
    """
    if not image_url:
        return

    try:
        UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filename = os.path.basename(image_url)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        logger.error(f"Image deletion error: {e}")
    return False
