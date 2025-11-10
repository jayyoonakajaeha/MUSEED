from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)

@router.post("/listen", response_model=schemas.ListeningHistory)
def record_listening_event(
    history: schemas.ListeningHistoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_listening_history(db=db, history=history, user_id=current_user.id)
