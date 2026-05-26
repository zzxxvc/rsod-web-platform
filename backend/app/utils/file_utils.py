import os
from app.config import settings


def ensure_directories():
    """确保必要的目录存在"""
    # settings中的路径已经是绝对路径
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)


async def save_upload_file(file, destination_dir):
    """保存上传的文件"""
    ensure_directories()
    filename = f"temp_{os.urandom(16).hex()}.jpg"
    file_path = os.path.join(destination_dir, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return filename


def get_file_url(filename, subdir):
    """获取文件的访问URL"""
    return f"/{subdir}/{filename}"