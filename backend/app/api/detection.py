import logging
import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.detection_service import detection_service
from app.utils.file_utils import save_upload_file, ensure_directories
from app.config import settings
from app.models.schemas import (
    SingleDetectionResponse,
    HistoryResponse,
    TargetListResponse,
    TargetItem,
    HistoryItem,
)

router = APIRouter(prefix="/detection", tags=["detection"])
logger = logging.getLogger(__name__)

ensure_directories()

DETECTION_HISTORY = []
DETECTION_RESULT_STORAGE = {}


@router.get("/status")
async def detection_status():
    ok, message = detection_service.readiness()
    return {"ready": ok, "message": message, "model_path": settings.YOLO_MODEL_PATH}


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("pest-v1")
):
    ok, message = detection_service.readiness()
    if not ok:
        raise HTTPException(status_code=503, detail=message)

    if not file.filename:
        raise HTTPException(status_code=400, detail="未收到文件，请使用字段名 file 上传图片")

    try:
        saved = await save_upload_file(file, settings.UPLOAD_DIR)
        logger.info(
            "收到上传: field=%s upload_name=%s saved=%s",
            "file",
            file.filename,
            saved.absolute_path,
        )
        result = detection_service.detect_single_image(saved.absolute_path, model_name)

        history_item = HistoryItem(
            id=result.detection_id,
            image_url=result.image_url,
            result_image_url=result.result_image_url,
            total_objects=len(result.boxes),
            created_at=result.created_at,
            model_name=result.model_name,
        )
        DETECTION_HISTORY.append(history_item)
        DETECTION_RESULT_STORAGE[result.detection_id] = result
        
        return SingleDetectionResponse(
            success=True,
            message="检测成功",
            data=result
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("单图检测失败")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/history", response_model=HistoryResponse)
async def get_detection_history():
    return HistoryResponse(
        success=True,
        message="获取成功",
        data=DETECTION_HISTORY,
        total=len(DETECTION_HISTORY)
    )


@router.get("/detail/{detection_id}", response_model=SingleDetectionResponse)
async def get_detection_detail(detection_id: str):
    result = DETECTION_RESULT_STORAGE.get(detection_id)
    if not result:
        raise HTTPException(status_code=404, detail="检测记录未找到")
    return SingleDetectionResponse(
        success=True,
        message="获取成功",
        data=result
    )


@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    targets = [
        TargetItem(id=0, name="airplane", chinese_name="飞机", description="固定翼飞机、直升机等"),
        TargetItem(id=1, name="oil_tank", chinese_name="油罐", description="储油罐、化工罐等"),
        TargetItem(id=2, name="playground", chinese_name="操场", description="运动场、操场等"),
        TargetItem(id=3, name="building", chinese_name="建筑物", description="各类建筑物"),
        TargetItem(id=4, name="ship", chinese_name="船舶", description="各类船舶"),
        TargetItem(id=5, name="pest", chinese_name="农业虫害", description="农作物病虫害"),
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )