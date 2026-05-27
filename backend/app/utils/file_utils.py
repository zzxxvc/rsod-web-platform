import os
from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class SavedUpload:
    """磁盘绝对路径（给 YOLO）+ 仅文件名（给静态 URL）。"""

    absolute_path: str
    filename: str


def ensure_directories():
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)


def _extension_from_upload(file) -> str:
    name = getattr(file, "filename", None) or ""
    ext = os.path.splitext(os.path.basename(name))[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        return ".jpg" if ext == ".jpeg" else ext
    content_type = getattr(file, "content_type", "") or ""
    if "png" in content_type:
        return ".png"
    if "webp" in content_type:
        return ".webp"
    return ".jpg"


async def save_upload_file(file, destination_dir: str) -> SavedUpload:
    """
    保存 multipart 上传的二进制内容。
    返回绝对路径供推理使用；禁止把 URL 或客户端路径当作文件内容。
    """
    ensure_directories()
    dest_dir = os.path.abspath(destination_dir)
    os.makedirs(dest_dir, exist_ok=True)

    content = await file.read()
    if not content:
        raise ValueError("上传文件为空，请确认前端使用 FormData.append('file', file对象) 而非路径字符串")

    ext = _extension_from_upload(file)
    filename = f"temp_{os.urandom(16).hex()}{ext}"
    absolute_path = os.path.join(dest_dir, filename)

    with open(absolute_path, "wb") as f:
        f.write(content)

    if os.path.getsize(absolute_path) == 0:
        raise ValueError("保存后的图像文件大小为 0")

    return SavedUpload(absolute_path=absolute_path, filename=filename)


def get_file_url(filename: str, subdir: str) -> str:
    """返回浏览器可访问的相对 URL，绝不返回磁盘绝对路径。"""
    safe_name = os.path.basename(filename)
    return f"/{subdir.strip('/')}/{safe_name}"


def static_path_from_url(static_url: str) -> str:
    """将 /static/uploads/xxx.jpg 转为本地绝对路径。"""
    if not static_url:
        raise ValueError("无效的文件 URL")
    path = static_url.lstrip("/")
    if path.startswith("static/"):
        path = path[len("static/") :]
    return os.path.join(settings.STATIC_DIR, path)
