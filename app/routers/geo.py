from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import City, State

router = APIRouter()


@router.get("/states")
def list_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/cities")
def list_cities(state_id: int, db: Session = Depends(get_db)):
    return db.query(City).filter(City.state_id == state_id).order_by(City.name).all()
