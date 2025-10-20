from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Blackout, Establishment, Resource, User
from ..security import get_current_user

router = APIRouter()


class BlackoutCreate(BaseModel):
    establishment_id: int
    resource_id: int | None = None
    start_ts: datetime
    end_ts: datetime
    reason: str | None = None


@router.get("", response_model=list[BlackoutCreate])
def list_blackouts(establishment_id: int, db: Session = Depends(get_db)):
    return db.query(Blackout).filter(Blackout.establishment_id == establishment_id).all()


@router.post("", response_model=BlackoutCreate, status_code=201)
def create_blackout(
    body: BlackoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.end_ts <= body.start_ts:
        raise HTTPException(status_code=400, detail="end_ts must be after start_ts")
    if not db.get(Establishment, body.establishment_id):
        raise HTTPException(status_code=404, detail="Establishment not found")
    if body.resource_id and not db.get(Resource, body.resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")

    b = Blackout(**body.dict())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.delete("/{blackout_id}", status_code=204)
def delete_blackout(
    blackout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = db.get(Blackout, blackout_id)
    if not b:
        raise HTTPException(status_code=404, detail="Blackout not found")
    db.delete(b)
    db.commit()
    return
