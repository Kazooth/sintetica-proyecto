from collections.abc import Sequence
from typing import Any, ClassVar
from starlette.requests import Request

from fastapi import FastAPI
from sqladmin import Admin, ModelView, action

from .db import SessionLocal, engine
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from .models import (
    City,
    Establishment,
    OpeningHour,
    Product,
    ProductCategory,
    Reservation,
    Resource,
    Sale,
    SaleItem,
    State,
    User,
)


class EstablishmentAdmin(ModelView, model=Establishment):
    column_list: ClassVar[Sequence] = [
        Establishment.id,
        Establishment.name,
        Establishment.address,
        Establishment.is_active,
    ]
    column_filters: ClassVar[Sequence] = [Establishment.is_active]

    async def delete_model(self, request: Request, pk: int) -> None:
        with SessionLocal() as s:
            obj = s.get(Establishment, pk)
            if obj is None:
                return
            # Si está activo, primero desactivar para seguridad
            if getattr(obj, "is_active", True):
                obj.is_active = False
                s.add(obj)
                s.commit()
                return
            # Si ya está inactivo, intentamos eliminar; si falla por FK, lo dejamos inactivo
            try:
                s.delete(obj)
                s.commit()
            except IntegrityError:
                s.rollback()
                obj.is_active = False
                s.add(obj)
                s.commit()

    @action("activate", "Activar", "¿Activar los establecimientos seleccionados?")
    def action_activate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(
                sa.update(Establishment).where(Establishment.id.in_(ids)).values(is_active=True)
            )
            s.commit()

    @action("deactivate", "Desactivar", "¿Desactivar los establecimientos seleccionados?")
    def action_deactivate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(
                sa.update(Establishment).where(Establishment.id.in_(ids)).values(is_active=False)
            )
            s.commit()

    @action(
        "purge_inactive",
        "Eliminar inactivos (selección)",
        "¿Eliminar físicamente los establecimientos INACTIVOS seleccionados?",
    )
    def action_purge_inactive(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            for _id in ids:
                obj = s.get(Establishment, _id)
                if obj is None or getattr(obj, "is_active", True):
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()

    @action(
        "purge_all_inactive",
        "Eliminar TODOS los inactivos",
        "¿Eliminar físicamente TODOS los establecimientos inactivos? Esta acción intentará eliminar uno por uno y omitirá los que tengan referencias.",
    )
    def action_purge_all_inactive(self, ids: list[int]) -> None:  # ids ignorados
        with SessionLocal() as s:
            inactive_ids = [
                row[0]
                for row in s.execute(
                    sa.select(Establishment.id).where(Establishment.is_active.is_(False))
                )
            ]
            for _id in inactive_ids:
                obj = s.get(Establishment, _id)
                if obj is None:
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()


class ResourceAdmin(ModelView, model=Resource):
    column_list: ClassVar[Sequence] = [
        Resource.id,
        Resource.establishment_id,
        Resource.name,
        Resource.kind,
        Resource.price_per_slot,
        Resource.slot_minutes,
        Resource.is_active,
    ]
    column_filters: ClassVar[Sequence] = [Resource.establishment_id, Resource.is_active]
    # Permitimos borrar, pero añadimos una acción segura de desactivación masiva.
    can_delete: ClassVar[bool] = True

    # Si el recurso tiene reservas asociadas, el borrado físico viola FK.
    # Sobrescribimos el delete para hacer 'soft delete' (is_active = False) si hay FK.
    async def delete_model(self, request: Request, pk: int) -> None:
        with SessionLocal() as s:
            obj = s.get(Resource, pk)
            if obj is None:
                return
            # Si está activo, primero desactivar (soft) y salir
            if getattr(obj, "is_active", True):
                obj.is_active = False
                s.add(obj)
                s.commit()
                return
            # Si ya está inactivo, intentamos eliminar
            try:
                s.delete(obj)
                s.commit()
            except IntegrityError:
                s.rollback()
                obj.is_active = False
                s.add(obj)
                s.commit()

    @action("activate", "Activar", "¿Activar los recursos seleccionados?")
    def action_activate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(sa.update(Resource).where(Resource.id.in_(ids)).values(is_active=True))
            s.commit()

    @action(
        "purge_inactive",
        "Eliminar inactivos (selección)",
        "¿Eliminar físicamente los recursos INACTIVOS seleccionados?",
    )
    def action_purge_inactive(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            for _id in ids:
                obj = s.get(Resource, _id)
                if obj is None or getattr(obj, "is_active", True):
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()

    @action(
        "purge_all_inactive",
        "Eliminar TODOS los inactivos",
        "¿Eliminar físicamente TODOS los recursos inactivos? Esta acción intentará eliminar uno por uno y omitirá los que tengan referencias.",
    )
    def action_purge_all_inactive(self, ids: list[int]) -> None:  # ids ignorados
        with SessionLocal() as s:
            inactive_ids = [
                row[0]
                for row in s.execute(sa.select(Resource.id).where(Resource.is_active.is_(False)))
            ]
            for _id in inactive_ids:
                obj = s.get(Resource, _id)
                if obj is None:
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()

    # Acción de admin para desactivar (soft-delete) uno o varios recursos
    @action("deactivate", "Desactivar", "¿Desactivar los recursos seleccionados?")
    def action_deactivate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(sa.update(Resource).where(Resource.id.in_(ids)).values(is_active=False))
            s.commit()


class OpeningHourAdmin(ModelView, model=OpeningHour):
    column_list: ClassVar[Sequence] = [
        OpeningHour.id,
        OpeningHour.establishment_id,
        OpeningHour.weekday,
        OpeningHour.open_time,
        OpeningHour.close_time,
    ]


class ReservationAdmin(ModelView, model=Reservation):
    name = "Reserva"
    name_plural = "Reservas"
    icon = "fa-solid fa-calendar-check"

    # Columnas visibles en la tabla de la lista:
    column_list: ClassVar[Sequence] = [
        Reservation.id,
        Reservation.resource_id,
        Reservation.user_id,
        Reservation.start_ts,
        Reservation.end_ts,
        Reservation.status,
        Reservation.total_price,
        Reservation.channel,
    ]

    # Campos que se mostrarán en el formulario de crear/editar:
    form_columns: ClassVar[Sequence] = [
        Reservation.resource_id,  # <- ID de la cancha
        Reservation.user_id,  # <- ID del usuario (cliente)
        Reservation.start_ts,
        Reservation.end_ts,
        Reservation.status,
        Reservation.channel,
        Reservation.total_price,  # lo calcularemos al guardar; igual lo dejamos visible por si quieres ver el valor
    ]

    # Choices para status y canal (evita escribir mal):
    form_choices: ClassVar[dict] = {
        "status": [
            ("PENDING", "PENDING"),
            ("CONFIRMED", "CONFIRMED"),
            ("CANCELLED", "CANCELLED"),
        ],
        "channel": [
            ("WEB", "WEB"),
            ("PHONE", "PHONE"),
            ("WALKIN", "WALKIN"),
            ("WHATSAPP", "WHATSAPP"),
        ],
    }

    # Cálculo automático del total antes de guardar (sync DB dentro de hook async)
    async def on_model_change(
        self,
        data: dict[Any, Any],
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        if (
            getattr(model, "resource_id", None)
            and getattr(model, "start_ts", None)
            and getattr(model, "end_ts", None)
        ):
            minutes = (model.end_ts - model.start_ts).total_seconds() / 60.0
            with SessionLocal() as s:
                res = s.get(Resource, model.resource_id)
                if res is not None and res.slot_minutes is not None:
                    # Opcional: validar múltiplo exacto
                    if minutes % float(res.slot_minutes) != 0:
                        raise ValueError(
                            f"La duración ({minutes} min) no es múltiplo de {res.slot_minutes} min."
                        )
                    # cálculo del total
                    if res.price_per_slot is not None:
                        slots = minutes / float(res.slot_minutes)
                        model.total_price = int(round(slots * res.price_per_slot))


class StateAdmin(ModelView, model=State):
    column_list: ClassVar[Sequence] = [State.id, State.name]


class CityAdmin(ModelView, model=City):
    column_list: ClassVar[Sequence] = [City.id, City.name, City.state_id]


class UserAdmin(ModelView, model=User):
    # first_name/last_name are convenience @property on User that delegate to Person.
    # sqladmin expects column-like descriptors or string names; use strings so it resolves at runtime.
    column_list: ClassVar[Sequence] = [User.id, User.email, "first_name", "last_name"]
    column_searchable_list: ClassVar[Sequence[str]] = [
        "email",
        "first_name",
        "last_name",
    ]


class ProductAdmin(ModelView, model=Product):
    column_list: ClassVar[Sequence] = [
        Product.id,
        Product.establishment_id,
        Product.name,
        Product.price,
        Product.tax_rate,
        Product.is_active,
    ]
    column_searchable_list: ClassVar[Sequence] = [Product.name]
    column_filters: ClassVar[Sequence] = [Product.establishment_id, Product.is_active]

    # Productos con ventas/inventario referenciándolos no pueden borrarse físicamente.
    # Hacemos soft delete si el DELETE choca con FK.
    async def delete_model(self, request: Request, pk: int) -> None:
        with SessionLocal() as s:
            obj = s.get(Product, pk)
            if obj is None:
                return
            if getattr(obj, "is_active", True):
                obj.is_active = False
                s.add(obj)
                s.commit()
                return
            try:
                s.delete(obj)
                s.commit()
            except IntegrityError:
                s.rollback()
                obj.is_active = False
                s.add(obj)
                s.commit()

    @action("activate", "Activar", "¿Activar los productos seleccionados?")
    def action_activate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(sa.update(Product).where(Product.id.in_(ids)).values(is_active=True))
            s.commit()

    @action("deactivate", "Desactivar", "¿Desactivar los productos seleccionados?")
    def action_deactivate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(sa.update(Product).where(Product.id.in_(ids)).values(is_active=False))
            s.commit()

    @action(
        "purge_inactive",
        "Eliminar inactivos (selección)",
        "¿Eliminar físicamente los productos INACTIVOS seleccionados?",
    )
    def action_purge_inactive(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            for _id in ids:
                obj = s.get(Product, _id)
                if obj is None or getattr(obj, "is_active", True):
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()

    @action(
        "purge_all_inactive",
        "Eliminar TODOS los inactivos",
        "¿Eliminar físicamente TODOS los productos inactivos? Esta acción intentará eliminar uno por uno y omitirá los que tengan referencias.",
    )
    def action_purge_all_inactive(self, ids: list[int]) -> None:  # ids ignorados
        with SessionLocal() as s:
            inactive_ids = [
                row[0]
                for row in s.execute(sa.select(Product.id).where(Product.is_active.is_(False)))
            ]
            for _id in inactive_ids:
                obj = s.get(Product, _id)
                if obj is None:
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()


class ProductCategoryAdmin(ModelView, model=ProductCategory):
    column_list: ClassVar[Sequence] = [
        ProductCategory.id,
        ProductCategory.name,
        ProductCategory.is_active,
    ]
    column_filters: ClassVar[Sequence] = [ProductCategory.is_active]

    async def delete_model(self, request: Request, pk: int) -> None:
        with SessionLocal() as s:
            obj = s.get(ProductCategory, pk)
            if obj is None:
                return
            if getattr(obj, "is_active", True):
                obj.is_active = False
                s.add(obj)
                s.commit()
                return
            try:
                s.delete(obj)
                s.commit()
            except IntegrityError:
                s.rollback()
                obj.is_active = False
                s.add(obj)
                s.commit()

    @action("activate", "Activar", "¿Activar las categorías seleccionadas?")
    def action_activate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(
                sa.update(ProductCategory).where(ProductCategory.id.in_(ids)).values(is_active=True)
            )
            s.commit()

    @action("deactivate", "Desactivar", "¿Desactivar las categorías seleccionadas?")
    def action_deactivate(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            s.execute(
                sa.update(ProductCategory)
                .where(ProductCategory.id.in_(ids))
                .values(is_active=False)
            )
            s.commit()

    @action(
        "purge_inactive",
        "Eliminar inactivos (selección)",
        "¿Eliminar físicamente las categorías INACTIVAS seleccionadas?",
    )
    def action_purge_inactive(self, ids: list[int]) -> None:
        with SessionLocal() as s:
            for _id in ids:
                obj = s.get(ProductCategory, _id)
                if obj is None or getattr(obj, "is_active", True):
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()

    @action(
        "purge_all_inactive",
        "Eliminar TODOS los inactivos",
        "¿Eliminar físicamente TODAS las categorías inactivas? Esta acción intentará eliminar uno por uno y omitirá los que tengan referencias.",
    )
    def action_purge_all_inactive(self, ids: list[int]) -> None:  # ids ignorados
        with SessionLocal() as s:
            inactive_ids = [
                row[0]
                for row in s.execute(
                    sa.select(ProductCategory.id).where(ProductCategory.is_active.is_(False))
                )
            ]
            for _id in inactive_ids:
                obj = s.get(ProductCategory, _id)
                if obj is None:
                    continue
                try:
                    s.delete(obj)
                    s.commit()
                except IntegrityError:
                    s.rollback()


class SaleAdmin(ModelView, model=Sale):
    column_list: ClassVar[Sequence] = [
        Sale.id,
        Sale.establishment_id,
        Sale.cashier_user_id,
        Sale.payment_method,
        Sale.subtotal,
        Sale.tax_total,
        Sale.grand_total,
        Sale.created_at,
    ]
    can_edit: ClassVar[bool] = False  # evita tocar venta cerrada
    can_delete: ClassVar[bool] = False


class SaleItemAdmin(ModelView, model=SaleItem):
    column_list: ClassVar[Sequence] = [
        SaleItem.id,
        SaleItem.sale_id,
        SaleItem.product_id,
        SaleItem.qty,
        SaleItem.unit_price,
        SaleItem.line_total,
    ]
    can_create: ClassVar[bool] = False
    can_edit: ClassVar[bool] = False
    can_delete: ClassVar[bool] = False


def init_admin(app: FastAPI):
    admin = Admin(app, engine, session_maker=SessionLocal)

    admin.add_view(StateAdmin)
    admin.add_view(CityAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(EstablishmentAdmin)
    admin.add_view(ResourceAdmin)
    admin.add_view(OpeningHourAdmin)
    admin.add_view(ReservationAdmin)
    admin.add_view(ProductCategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(SaleAdmin)
    admin.add_view(SaleItemAdmin)
