from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.qa_service import get_qa_answer

router = APIRouter(prefix="/qa", tags=["qa"])


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    处理皮肤病变问答请求
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        answer = await get_qa_answer(request.question)
        return QAResponse(answer=answer)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求出错: {str(e)}")
