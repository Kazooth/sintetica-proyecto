from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Reservation, Resource
from ..security import require_roles

router = APIRouter()


@router.get("/sales/summary")
def sales_summary(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles({"ADMIN", "OWNER"})),
):
    if date_to <= date_from:
        raise HTTPException(status_code=400, detail="date_to must be after date_from")

    # Use explicit SQL to avoid GROUP BY ambiguity across dialect/param styles
    rows = db.execute(
        text(
            """
            SELECT
                date_trunc('day', sales.created_at) AS day,
                sum(sales.subtotal) AS subtotal,
                sum(sales.tax_total) AS tax_total,
                sum(sales.grand_total) AS grand_total,
                count(sales.id) AS count
            FROM sales
            WHERE sales.created_at >= :date_from AND sales.created_at < :date_to
            GROUP BY 1
            ORDER BY 1
            """
        ),
        {"date_from": date_from, "date_to": date_to},
    ).mappings().all()
    return [
        {
            "day": r["day"].isoformat(),
            "subtotal": int(r["subtotal"] or 0),
            "tax_total": int(r["tax_total"] or 0),
            "grand_total": int(r["grand_total"] or 0),
            "count": int(r["count"] or 0),
        }
        for r in rows
    ]


@router.get("/resources/utilization")
def resource_utilization(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles({"ADMIN", "OWNER", "STAFF"})),
):
    if date_to <= date_from:
        raise HTTPException(status_code=400, detail="date_to must be after date_from")

    # Total minutos reservados por recurso en el rango
    rows = (
        db.query(
            Resource.id.label("resource_id"),
            func.sum(func.extract("epoch", Reservation.end_ts - Reservation.start_ts) / 60.0).label(
                "minutes"
            ),
        )
        .join(Resource, Resource.id == Reservation.resource_id)
        .filter(
            Reservation.status == "CONFIRMED",
            Reservation.start_ts < date_to,
            Reservation.end_ts > date_from,
        )
        .group_by(Resource.id)
        .order_by(Resource.id)
        .all()
    )
    return [{"resource_id": r.resource_id, "minutes": int(r.minutes or 0)} for r in rows]
