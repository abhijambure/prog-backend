from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_assistant import get_ai_reply

router = APIRouter(prefix="/chat", tags=["ai-assistant"])

@router.post("/", response_model=ChatResponse)
def chat_assistant(
    chat_in: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reply_data = get_ai_reply(
        db=db,
        user_id=current_user.id,
        message=chat_in.message,
        history=chat_in.history
    )
    return reply_data
