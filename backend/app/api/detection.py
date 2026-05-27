import logging
import os

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.services.detection_service import detection_service
from app.services.detection_store import (
    delete_record as delete_detection_record,
    get_detail,
    get_owned_record,
    list_history,
    save_detection,
)
from app.utils.file_utils import save_upload_file, ensure_directories, static_path_from_url
from app.config import settings
from app.models.schemas import (
    SingleDetectionResponse,
    HistoryResponse,
    TargetListResponse,
    TargetItem,
)
from database import get_db
from database.models import User

router = APIRouter(prefix="/detection", tags=["detection"])
logger = logging.getLogger(__name__)

ensure_directories()


@router.get("/status")
async def detection_status():
    ok, message = detection_service.readiness()
    return {"ready": ok, "message": message, "model_path": settings.YOLO_MODEL_PATH}


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("pest-v1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok, message = detection_service.readiness()
    if not ok:
        raise HTTPException(status_code=503, detail=message)

    if not file.filename:
        raise HTTPException(status_code=400, detail="未收到文件，请使用字段名 file 上传图片")

    try:
        saved = await save_upload_file(file, settings.UPLOAD_DIR)
        logger.info(
            "用户 %s 上传检测: %s -> %s",
            current_user.username,
            file.filename,
            saved.absolute_path,
        )
        result = detection_service.detect_single_image(saved.absolute_path, model_name)
        save_detection(db, current_user, result)

        return SingleDetectionResponse(
            success=True,
            message="检测成功",
            data=result,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("单图检测失败")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/history", response_model=HistoryResponse)
async def get_detection_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = list_history(db, current_user)
    return HistoryResponse(
        success=True,
        message="获取成功",
        data=items,
        total=len(items),
    )


@router.get("/detail/{detection_id}", response_model=SingleDetectionResponse)
async def get_detection_detail(
    detection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_detail(db, current_user, detection_id)
    if not result:
        raise HTTPException(status_code=404, detail="检测记录未找到或无权访问")
    return SingleDetectionResponse(
        success=True,
        message="获取成功",
        data=result,
    )


@router.get("/download/{detection_id}")
async def download_detection_result(
    detection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_owned_record(db, current_user, detection_id)
    if not record or not record.result_image_key:
        raise HTTPException(status_code=404, detail="检测记录未找到或无权下载")

    try:
        file_path = static_path_from_url(record.result_image_key)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的结果图路径")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="结果图文件不存在")

    download_name = f"detection_{detection_id[:8]}{os.path.splitext(file_path)[1] or '.jpg'}"
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=download_name,
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )


@router.delete("/{detection_id}")
async def delete_detection(
    detection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not delete_detection_record(db, current_user, detection_id):
        raise HTTPException(status_code=404, detail="检测记录未找到或无权删除")
    return {"success": True, "message": "删除成功"}


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
        data=targets,
    )
