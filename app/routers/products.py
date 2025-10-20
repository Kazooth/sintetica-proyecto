from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, User
from ..schemas import ProductOut
from ..security import require_roles

router = APIRouter()


# GET: productos activos por establecimiento
@router.get("", response_model=list[ProductOut])
def list_products(
    establishment_id: int,
    response: Response,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    base = db.query(Product).filter(Product.establishment_id == establishment_id, Product.is_active)
    total = base.count()
    items = base.order_by(Product.name).limit(limit).offset(offset).all()
    response.headers["X-Total-Count"] = str(total)
    return items


# POST: desactivar (soft delete)
@router.post("/{product_id}/deactivate", status_code=200)
def deactivate_product(
    product_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles({"ADMIN", "OWNER", "STAFF"})),
):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.is_active = False
    db.add(p)
    db.commit()
    return {"ok": True, "is_active": p.is_active}


# DELETE: borrar (hard delete)
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles({"ADMIN", "OWNER"})),
):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    return
