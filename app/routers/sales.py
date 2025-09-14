from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, Sale, SaleItem, User
from ..schemas import SaleCreate, SaleOut, SaleItemOut
from ..security import get_current_user

router = APIRouter()

# POST: crear venta (cálculo subtotal/IVA/total)
@router.post("", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items")

    product_ids = [it.product_id for it in payload.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

    subtotal = 0
    tax_total = 0
    line_items: list[SaleItem] = []

    for it in payload.items:
        p = products.get(it.product_id)
        if not p or not p.is_active:
            raise HTTPException(status_code=404, detail=f"Product {it.product_id} not found or inactive")
        if p.establishment_id != payload.establishment_id:
            raise HTTPException(status_code=400, detail=f"Product {p.id} not belongs to establishment {payload.establishment_id}")

        unit_price = p.price
        line_subtotal = unit_price * it.qty
        line_tax = int(round(line_subtotal * float(p.tax_rate)))
        line_total = line_subtotal + line_tax

        subtotal += line_subtotal
        tax_total += line_tax

        line_items.append(
            SaleItem(
                product_id=p.id,
                qty=it.qty,
                unit_price=unit_price,
                tax_rate=float(p.tax_rate),
                line_total=line_total,
            )
        )

    grand_total = subtotal + tax_total

    sale = Sale(
        establishment_id=payload.establishment_id,
        cashier_user_id=current_user.id,
        reservation_id=payload.reservation_id,
        payment_method=payload.payment_method,
        subtotal=subtotal,
        tax_total=tax_total,
        grand_total=grand_total,
    )
    db.add(sale)
    db.flush()  # sale.id

    for li in line_items:
        li.sale_id = sale.id
        db.add(li)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating sale")

    items_out = [
        SaleItemOut(
            product_id=li.product_id,
            qty=li.qty,
            unit_price=li.unit_price,
            tax_rate=li.tax_rate,
            line_total=li.line_total,
        )
        for li in line_items
    ]

    return SaleOut(
        id=sale.id,
        establishment_id=sale.establishment_id,
        cashier_user_id=sale.cashier_user_id,
        reservation_id=sale.reservation_id,
        payment_method=sale.payment_method,
        subtotal=sale.subtotal,
        tax_total=sale.tax_total,
        grand_total=sale.grand_total,
        items=items_out,
    )

# POST: anular venta (VOID) – opcional si tu tabla tiene columna 'status'
@router.post("/{sale_id}/void", status_code=200)
def void_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.get(Sale, sale_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Si tu tabla 'sales' no tiene columna 'status', comenta esto o agrega la columna con un ALTER.
    try:
        getattr(s, "status")
    except AttributeError:
        # Seguimos devolviendo 200 pero indicamos que no hay soporte
        return {"ok": False, "detail": "Column 'status' missing in sales table"}

    s.status = "VOID"
    db.add(s)
    db.commit()
    return {"ok": True, "status": s.status}
