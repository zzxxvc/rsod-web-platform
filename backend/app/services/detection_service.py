import logging
import os
import time
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

def _check_opencv() -> Tuple[bool, str]:
    try:
        import cv2
    except ImportError as e:
        return False, f"未安装 opencv-python: {e}"

    if not hasattr(cv2, "imwrite") or cv2.__file__ is None:
        return False, (
            "OpenCV 安装不完整（cv2 缺少 imwrite，多为 pip 安装中断或包冲突）。"
            "请执行: pip uninstall opencv-python opencv-contrib-python -y "
            "&& pip install opencv-python==4.11.0.86 "
            "&& pip install \"numpy>=1.23.0,<2.0.0\""
        )
    return True, "ok"


_CV_OK, _CV_MSG = _check_opencv()

try:
    if _CV_OK:
        from ultralytics import YOLO
        YOLO_IMPORT_ERROR = None
    else:
        YOLO = None
        YOLO_IMPORT_ERROR = RuntimeError(_CV_MSG)
except Exception as e:
    YOLO = None
    YOLO_IMPORT_ERROR = e

import cv2
from app.config import settings
from app.models.schemas import DetectionBox, DetectionResult
from app.utils.file_utils import get_file_url

logger = logging.getLogger(__name__)


class DetectionService:
    def __init__(self):
        self.model = None
        self.class_names = {}
        self._init_class_names()

    def readiness(self) -> Tuple[bool, str]:
        """返回 (是否可用, 说明)。"""
        cv_ok, cv_msg = _check_opencv()
        if not cv_ok:
            return False, cv_msg
        if YOLO is None:
            return False, (
                f"未安装或无法加载 ultralytics：{YOLO_IMPORT_ERROR}. "
                "请在 backend 目录执行: pip install -r requirements.txt"
            )
        if not os.path.exists(settings.YOLO_MODEL_PATH):
            return False, f"模型文件不存在: {settings.YOLO_MODEL_PATH}"
        return True, "ready"

    def _load_model(self):
        ok, msg = self.readiness()
        if not ok:
            raise RuntimeError(msg)
        self.model = YOLO(settings.YOLO_MODEL_PATH)
        if hasattr(self.model, "names") and self.model.names:
            self.class_names = dict(self.model.names)

    def _ensure_model_loaded(self):
        if self.model is None:
            self._load_model()

    def _init_class_names(self):
        self.class_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "airplane",
            5: "bus",
        }

    def detect_single_image(self, image_path: str, model_name: str = "pest-v1") -> DetectionResult:
        start_time = time.time()
        detection_id = str(uuid.uuid4())

        # YOLO 必须使用本机可读的文件绝对路径，不能用 /static/... URL
        image_path = os.path.abspath(os.path.normpath(image_path))
        if image_path.startswith(("http://", "https://", "/static/")):
            raise ValueError(
                f"无效的图像路径（疑似 URL 而非本地文件）: {image_path}。"
                "应由后端先保存上传文件再推理。"
            )
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")

        self._ensure_model_loaded()

        results = self.model.predict(
            source=image_path,
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            save=False,
        )
        if not results:
            raise RuntimeError("模型未返回检测结果")

        boxes: List[DetectionBox] = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.class_names.get(class_id, f"class_{class_id}")

                boxes.append(
                    DetectionBox(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                    )
                )

        result_filename = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(settings.RESULT_DIR, result_filename)

        annotated_image = results[0].plot()
        cv2.imwrite(result_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

        detection_time = time.time() - start_time

        return DetectionResult(
            detection_id=detection_id,
            image_url=get_file_url(os.path.basename(image_path), "static/uploads"),
            result_image_url=get_file_url(result_filename, "static/results"),
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(detection_time, 3),
            model_name=model_name,
            created_at=datetime.now(),
        )


detection_service = DetectionService()
