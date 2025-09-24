from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Establishment
from ..schemas import EstablishmentOut

router = APIRouter()


@router.get("", response_model=list[EstablishmentOut])
def list_establishments(db: Session = Depends(get_db)):
    return db.query(Establishment).order_by(Establishment.name).all()
