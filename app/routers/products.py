from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, User
from ..schemas import ProductOut
from ..security import get_current_user

router = APIRouter()


# GET: productos activos por establecimiento
@router.get("", response_model=list[ProductOut])
def list_products(establishment_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Product)
        .filter(Product.establishment_id == establishment_id, Product.is_active)
        .order_by(Product.name)
        .all()
    )


# POST: desactivar (soft delete)
@router.post("/{product_id}/deactivate", status_code=200)
def deactivate_product(
    product_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    return
