from datetime import datetime, time

from pydantic import BaseModel, EmailStr, Field


class EstablishmentOut(BaseModel):
    id: int
    name: str
    address: str | None = None

    class Config:
        from_attributes = True


class ResourceOut(BaseModel):
    id: int
    name: str
    kind: str | None
    price_per_slot: int | None
    slot_minutes: int | None
    is_active: bool

    class Config:
        from_attributes = True


class OpeningHourOut(BaseModel):
    weekday: int
    open_time: time
    close_time: time

    class Config:
        from_attributes = True


class ReservationOut(BaseModel):
    id: int
    resource_id: int
    user_id: int
    start_ts: datetime
    end_ts: datetime
    status: str
    total_price: int

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    tax_rate: float

    class Config:
        from_attributes = True


class SaleItemIn(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class SaleItemOut(BaseModel):
    product_id: int
    qty: int
    unit_price: int
    tax_rate: float
    line_total: int

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    establishment_id: int
    cashier_user_id: int
    reservation_id: int | None
    payment_method: str
    subtotal: int
    tax_total: int
    grand_total: int
    items: list[SaleItemOut]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str | None = None
    last_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReservationCreate(BaseModel):
    resource_id: int
    start_ts: datetime
    end_ts: datetime
    channel: str = "WEB"


class SaleCreate(BaseModel):
    establishment_id: int
    payment_method: str = Field(pattern="^(CASH|CARD|TRANSFER)$")
    reservation_id: int | None = None
    items: list[SaleItemIn]
