from datetime import datetime, timedelta, time

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..security import get_current_user
from ..models import Reservation, Resource, OpeningHour, Blackout, User
from ..schemas import ReservationOut, ReservationCreate

router = APIRouter()

# GET: reservas CONFIRMED de un recurso en un día
@router.get("", response_model=list[ReservationOut])
def reservations_of_day(resource_id: int, date: str, db: Session = Depends(get_db)):
    try:
        day = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date. Use YYYY-MM-DD")
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return db.execute(
        select(Reservation).where(
            Reservation.resource_id == resource_id,
            Reservation.status == "CONFIRMED",
            Reservation.start_ts < end,
            Reservation.end_ts > start,
        )
    ).scalars().all()

# POST: crear reserva con validaciones (horarios, blackouts, múltiplo, precio)
@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(
    body: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.end_ts <= body.start_ts:
        raise HTTPException(status_code=400, detail="end_ts must be after start_ts")

    res = db.get(Resource, body.resource_id)
    if not res or not res.is_active:
        raise HTTPException(status_code=404, detail="Resource not found or inactive")
    if not res.slot_minutes or not res.price_per_slot:
        raise HTTPException(status_code=400, detail="Resource lacks pricing config")

    minutes = (body.end_ts - body.start_ts).total_seconds() / 60.0
    if minutes % float(res.slot_minutes) != 0:
        raise HTTPException(status_code=400, detail=f"Duration must be multiple of {res.slot_minutes} minutes")

    # Opening hours del día
    dow = body.start_ts.isoweekday()  # 1..7
    oh = (
        db.query(OpeningHour)
        .filter(OpeningHour.establishment_id == res.establishment_id, OpeningHour.weekday == dow)
        .first()
    )
    if not oh:
        raise HTTPException(status_code=400, detail="Establishment closed this day")

    def _mins(t: time) -> int: return t.hour * 60 + t.minute
    start_m = body.start_ts.hour * 60 + body.start_ts.minute
    end_m = body.end_ts.hour * 60 + body.end_ts.minute
    if not (_mins(oh.open_time) <= start_m and end_m <= _mins(oh.close_time)):
        raise HTTPException(status_code=400, detail="Reservation outside opening hours")

    # Blackouts (del establecimiento o del recurso)
    overlap = and_(Blackout.start_ts < body.end_ts, Blackout.end_ts > body.start_ts)
    blk = (
        db.query(Blackout)
        .filter(
            Blackout.establishment_id == res.establishment_id,
            overlap,
            or_(Blackout.resource_id == None, Blackout.resource_id == res.id),
        )
        .first()
    )
    if blk:
        raise HTTPException(status_code=409, detail="Time blocked by blackout")

    # Precio
    slots = minutes / float(res.slot_minutes)
    total_price = int(round(slots * res.price_per_slot))

    # Insertar (DB bloquea solape por constraint)
    new_r = Reservation(
        resource_id=body.resource_id,
        user_id=current_user.id,
        start_ts=body.start_ts,
        end_ts=body.end_ts,
        status="CONFIRMED",
        total_price=total_price,
        channel=body.channel,
    )
    db.add(new_r)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "reservations_no_overlap" in str(e.orig):
            raise HTTPException(status_code=409, detail="Time slot overlaps another reservation")
        raise
    db.refresh(new_r)
    return new_r

# POST: cancelar (soft delete)
@router.post("/{reservation_id}/cancel", status_code=200)
def cancel_reservation(
    reservation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.status == "CANCELLED":
        return {"ok": True, "status": r.status}
    r.status = "CANCELLED"
    db.add(r)
    db.commit()
    return {"ok": True, "status": r.status}

# DELETE: borrar físicamente (úsalo con cuidado)
@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(
    reservation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(r)
    db.commit()
    return
