import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import Date, cast, distinct, func
from sqlalchemy.orm import Session

from app.models.schemas import DetectionBox, DetectionResult, HistoryItem
from database.models import DetectionRecord, DetectionResult as DetectionResultRow, User

HIGH_RISK_CONFIDENCE = 0.8


def _parse_id(detection_id: str) -> UUID:
    try:
        return UUID(detection_id)
    except ValueError:
        raise ValueError("无效的记录 ID")


def save_detection(
    db: Session,
    user: User,
    result: DetectionResult,
    record_type: str = "single",
) -> DetectionRecord:
    record_id = _parse_id(result.detection_id)
    record = DetectionRecord(
        id=record_id,
        user_id=user.id,
        type=record_type,
        status="completed",
        model_name=result.model_name,
        total_objects=result.total_objects,
        detection_time=result.detection_time,
        original_image_key=result.image_url,
        result_image_key=result.result_image_url,
    )
    db.add(record)
    for box in result.boxes:
        db.add(
            DetectionResultRow(
                record_id=record_id,
                x1=box.x1,
                y1=box.y1,
                x2=box.x2,
                y2=box.y2,
                confidence=box.confidence,
                class_id=box.class_id,
                class_name=box.class_name,
            )
        )
    db.commit()
    db.refresh(record)
    return record


def list_history(db: Session, user: User) -> List[HistoryItem]:
    records = (
        db.query(DetectionRecord)
        .filter(DetectionRecord.user_id == user.id)
        .order_by(DetectionRecord.created_at.desc())
        .all()
    )
    return [
        HistoryItem(
            id=str(r.id),
            image_url=r.original_image_key or "",
            result_image_url=r.result_image_key or "",
            total_objects=r.total_objects or 0,
            created_at=r.created_at,
            model_name=r.model_name,
        )
        for r in records
    ]


def get_owned_record(db: Session, user: User, detection_id: str) -> Optional[DetectionRecord]:
    rid = _parse_id(detection_id)
    return (
        db.query(DetectionRecord)
        .filter(DetectionRecord.id == rid, DetectionRecord.user_id == user.id)
        .first()
    )


def get_detail(db: Session, user: User, detection_id: str) -> Optional[DetectionResult]:
    record = get_owned_record(db, user, detection_id)
    if not record:
        return None
    rows = (
        db.query(DetectionResultRow)
        .filter(DetectionResultRow.record_id == record.id)
        .all()
    )
    boxes = [
        DetectionBox(
            x1=r.x1,
            y1=r.y1,
            x2=r.x2,
            y2=r.y2,
            confidence=r.confidence,
            class_id=r.class_id,
            class_name=r.class_name,
        )
        for r in rows
    ]
    return DetectionResult(
        detection_id=str(record.id),
        image_url=record.original_image_key or "",
        result_image_url=record.result_image_key or "",
        boxes=boxes,
        total_objects=record.total_objects or 0,
        detection_time=record.detection_time or 0.0,
        model_name=record.model_name,
        created_at=record.created_at,
    )


def delete_record(db: Session, user: User, detection_id: str) -> bool:
    record = get_owned_record(db, user, detection_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def get_user_stats(db: Session, user: User) -> Dict[str, Any]:
    """个人中心统计（仅当前用户）。"""
    uid = user.id

    total_diagnoses = (
        db.query(DetectionRecord)
        .filter(DetectionRecord.user_id == uid, DetectionRecord.status == "completed")
        .count()
    )

    high_risk_cases = (
        db.query(DetectionRecord.id)
        .join(DetectionResultRow, DetectionResultRow.record_id == DetectionRecord.id)
        .filter(
            DetectionRecord.user_id == uid,
            DetectionResultRow.confidence >= HIGH_RISK_CONFIDENCE,
        )
        .distinct()
        .count()
    )

    avg_conf = (
        db.query(func.avg(DetectionResultRow.confidence))
        .join(DetectionRecord, DetectionRecord.id == DetectionResultRow.record_id)
        .filter(DetectionRecord.user_id == uid)
        .scalar()
    )
    average_accuracy = round(float(avg_conf or 0) * 100, 1)

    active_days = (
        db.query(func.count(distinct(cast(DetectionRecord.created_at, Date))))
        .filter(DetectionRecord.user_id == uid)
        .scalar()
    ) or 0
    if active_days > 0:
        usage_days = int(active_days)
    elif user.created_at:
        usage_days = max(1, (datetime.utcnow() - user.created_at).days + 1)
    else:
        usage_days = 1

    return {
        "total_diagnoses": total_diagnoses,
        "high_risk_cases": high_risk_cases,
        "average_accuracy": average_accuracy,
        "usage_days": usage_days,
    }
