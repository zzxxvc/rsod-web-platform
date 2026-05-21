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

ensure_directories()

DETECTION_HISTORY = []
DETECTION_RESULT_STORAGE = {}


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("pest-v1")
):
    try:
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        image_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        result = detection_service.detect_single_image(image_path, model_name)

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
    except Exception as e:
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