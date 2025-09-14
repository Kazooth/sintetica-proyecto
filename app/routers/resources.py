from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Resource, OpeningHour
from ..schemas import ResourceOut, OpeningHourOut

router = APIRouter()

@router.get("", response_model=list[ResourceOut])
def list_resources(establishment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Resource)
        .filter(Resource.establishment_id == establishment_id, Resource.is_active == True)
        .order_by(Resource.name)
        .all()
    )

@router.get("/opening-hours", response_model=list[OpeningHourOut])
def get_opening_hours(establishment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(OpeningHour)
        .filter(OpeningHour.establishment_id == establishment_id)
        .order_by(OpeningHour.weekday, OpeningHour.open_time)
        .all()
    )