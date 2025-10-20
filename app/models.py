# backend/app/models.py
from datetime import date, datetime, time

import sqlalchemy as sa
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Si más adelante quieres reflejar UNIQUE/INDEX del SQL, puedes añadir UniqueConstraint/Index.


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    document_number: Mapped[str | None] = mapped_column(String(40))
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # index hint: email is often searched
    # make email indexed and unique at DB level
    __table_args__ = (
        sa.Index("ix_persons_email", "email"),
        sa.UniqueConstraint("email", name="uq_persons_email"),
    )


# (no duplicate Base)


# --- Ubicación ---
class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"))
    __table_args__ = (sa.UniqueConstraint("name", "state_id", name="uq_city_name_state"),)


# --- Seguridad / Personas ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    # relationship to Person for easy access
    person: Mapped["Person"] = relationship("Person", lazy="joined")
    # valores: ADMIN/OWNER/STAFF/CUSTOMER (tu SQL lo fija con CHECK y default)
    role: Mapped[str] = mapped_column(String(20))

    # convenience properties so existing code can keep using user.first_name / last_name
    @property
    def first_name(self) -> str | None:
        return getattr(self.person, "first_name", None)

    @property
    def last_name(self) -> str | None:
        return getattr(self.person, "last_name", None)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str | None] = mapped_column(Text())


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text())


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), primary_key=True)


# --- Negocio base ---
class Establishment(Base):
    __tablename__ = "establishments"
    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(160))
    __table_args__ = (sa.UniqueConstraint("name", "city_id", name="uq_establishment_name_city"),)
    phone: Mapped[str | None] = mapped_column(String(40))
    address: Mapped[str | None] = mapped_column(String(200))


class EstablishmentStaff(Base):
    __tablename__ = "establishment_staff"
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str | None] = mapped_column(String(60))
    capacity: Mapped[int | None]
    slot_minutes: Mapped[int | None]
    price_per_slot: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(8))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (sa.UniqueConstraint("establishment_id", "name", name="uq_resource_est_name"),)


class OpeningHour(Base):
    __tablename__ = "opening_hours"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    weekday: Mapped[int]
    open_time: Mapped[time]  # TIME en SQL
    close_time: Mapped[time]
    __table_args__ = (
        sa.UniqueConstraint("establishment_id", "weekday", name="uq_opening_est_weekday"),
    )


class Blackout(Base):
    __tablename__ = "blackouts"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    resource_id: Mapped[int | None] = mapped_column(ForeignKey("resources.id"))
    # En SQL son TIMESTAMPTZ:
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None] = mapped_column(String(200))


class PricingRule(Base):
    __tablename__ = "pricing_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    resource_id: Mapped[int | None] = mapped_column(ForeignKey("resources.id"))
    weekday: Mapped[int | None]
    start_time: Mapped[time]  # TIME en SQL
    end_time: Mapped[time]
    price_per_slot: Mapped[int]
    # -> DATE, no timestamptz
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[int | None]


# --- Reservas / Eventos ---
# backend/app/models.py  (solo fragmento)
class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # ← AGREGA ESTO
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str]
    total_price: Mapped[int]
    channel: Mapped[str | None]


class ReservationPayment(Base):
    __tablename__ = "reservation_payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    amount: Mapped[int]
    method: Mapped[str]
    # TIMESTAMPTZ + default now()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(Text())


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    name: Mapped[str] = mapped_column(String(160))
    # TIMESTAMPTZ en SQL:
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    affects_pricing: Mapped[bool] = mapped_column(Boolean, default=False)
    blocks_booking: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text())


# --- Kiosko / Inventario / Ventas ---
class ProductCategory(Base):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"))
    name: Mapped[str] = mapped_column(String(160))
    price: Mapped[int]
    tax_rate: Mapped[float] = mapped_column(Numeric(4, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # sku nuevo (nullable + unique)
    sku: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    __table_args__ = (sa.UniqueConstraint("establishment_id", "name", name="uq_product_est_name"),)


class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int]
    # TIMESTAMPTZ en SQL:
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryTx(Base):
    __tablename__ = "inventory_tx"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int]
    tx_type: Mapped[str]  # IN/OUT/ADJUST/WASTAGE (CHECK en SQL)
    reason: Mapped[str | None] = mapped_column(String(200))
    sale_item_id: Mapped[int | None]
    # TIMESTAMPTZ en SQL:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"))
    cashier_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # En tu SQL has dejado ON DELETE SET NULL — reflejamos eso:
    reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservations.id", ondelete="SET NULL")
    )
    payment_method: Mapped[str] = mapped_column(String(20))  # CHECK en SQL
    subtotal: Mapped[int]
    tax_total: Mapped[int]
    grand_total: Mapped[int]
    status: Mapped[str] = mapped_column(String(10), default="OK")
    # TIMESTAMPTZ en SQL:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SaleItem(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int]
    unit_price: Mapped[int]
    tax_rate: Mapped[float] = mapped_column(Numeric(4, 2))
    line_total: Mapped[int]
