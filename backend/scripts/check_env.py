#!/usr/bin/env python3
"""检查检测相关依赖是否可用。在 backend 目录执行: python scripts/check_env.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    errors = []

    try:
        import cv2

        print(f"opencv: {cv2.__version__} @ {cv2.__file__}")
        if not hasattr(cv2, "imwrite"):
            errors.append("cv2 缺少 imwrite，OpenCV 安装损坏，需重装 opencv-python")
    except ImportError as e:
        errors.append(f"未安装 opencv-python: {e}")

    try:
        import numpy as np

        print(f"numpy: {np.__version__}")
        if tuple(int(x) for x in np.__version__.split(".")[:2]) >= (2, 0):
            errors.append("numpy>=2 可能与 ultralytics 冲突，建议 pip install \"numpy>=1.23.0,<2.0.0\"")
    except ImportError as e:
        errors.append(f"未安装 numpy: {e}")

    try:
        from ultralytics import YOLO

        print("ultralytics: OK")
        from app.config import settings
        import os

        if os.path.exists(settings.YOLO_MODEL_PATH):
            print(f"model: {settings.YOLO_MODEL_PATH}")
        else:
            errors.append(f"模型不存在: {settings.YOLO_MODEL_PATH}")
    except Exception as e:
        errors.append(f"ultralytics 不可用: {e}")

    if errors:
        print("\n问题:")
        for msg in errors:
            print(f"  - {msg}")
        print(
            "\n修复建议:\n"
            "  pip uninstall opencv-python opencv-contrib-python -y\n"
            "  pip install opencv-python==4.11.0.86\n"
            '  pip install "numpy>=1.23.0,<2.0.0"\n'
        )
        return 1

    print("\n环境检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
