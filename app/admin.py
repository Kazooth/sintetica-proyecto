from fastapi import FastAPI
from sqladmin import Admin, ModelView
from .db import engine, SessionLocal
from .models import Establishment, Resource, OpeningHour, Reservation
from .models import ProductCategory, Product, Sale, SaleItem
from .models import State, City, User


class EstablishmentAdmin(ModelView, model=Establishment):
    column_list = [Establishment.id, Establishment.name, Establishment.address]

class ResourceAdmin(ModelView, model=Resource):
    column_list = [Resource.id, Resource.establishment_id, Resource.name, Resource.kind, Resource.price_per_slot, Resource.slot_minutes, Resource.is_active]

class OpeningHourAdmin(ModelView, model=OpeningHour):
    column_list = [OpeningHour.id, OpeningHour.establishment_id, OpeningHour.weekday, OpeningHour.open_time, OpeningHour.close_time]

class ReservationAdmin(ModelView, model=Reservation):
    name = "Reserva"
    name_plural = "Reservas"
    icon = "fa-solid fa-calendar-check"

    # Columnas visibles en la tabla de la lista:
    column_list = [
        Reservation.id, Reservation.resource_id, Reservation.user_id,
        Reservation.start_ts, Reservation.end_ts, Reservation.status,
        Reservation.total_price, Reservation.channel
    ]

    # Campos que se mostrarán en el formulario de crear/editar:
    form_columns = [
        Reservation.resource_id,   # <- ID de la cancha
        Reservation.user_id,       # <- ID del usuario (cliente)
        Reservation.start_ts,
        Reservation.end_ts,
        Reservation.status,
        Reservation.channel,
        Reservation.total_price,   # lo calcularemos al guardar; igual lo dejamos visible por si quieres ver el valor
    ]

    # Choices para status y canal (evita escribir mal):
    form_choices = {
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

    # Cálculo automático del total antes de guardar
    # (usa SessionLocal; pasaremos session_maker al Admin más abajo)
    def on_model_change(self, form, model, is_created):
        if model.resource_id and model.start_ts and model.end_ts:
            with SessionLocal() as s:
                res = s.get(Resource, model.resource_id)
                if res and res.slot_minutes:
                    minutes = (model.end_ts - model.start_ts).total_seconds() / 60.0
                # Opcional: validar múltiplo exacto
                    if (minutes % float(res.slot_minutes)) != 0:
                        raise ValueError(f"La duración ({minutes} min) no es múltiplo de {res.slot_minutes} min.")
                # cálculo del total
                if res.price_per_slot:
                    slots = minutes / float(res.slot_minutes)
                    model.total_price = int(round(slots * res.price_per_slot))

class StateAdmin(ModelView, model=State):
    column_list = [State.id, State.name]

class CityAdmin(ModelView, model=City):
    column_list = [City.id, City.name, City.state_id]

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.first_name, User.last_name]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    
class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.establishment_id, Product.name, Product.price, Product.tax_rate, Product.is_active]
    column_searchable_list = [Product.name]
    
class ProductCategoryAdmin(ModelView, model=ProductCategory):
    column_list = [ProductCategory.id, ProductCategory.name]

class SaleAdmin(ModelView, model=Sale):
    column_list = [Sale.id, Sale.establishment_id, Sale.cashier_user_id, Sale.payment_method, Sale.subtotal, Sale.tax_total, Sale.grand_total, Sale.created_at]
    can_edit = False  # evita tocar venta cerrada
    can_delete = False

class SaleItemAdmin(ModelView, model=SaleItem):
    column_list = [SaleItem.id, SaleItem.sale_id, SaleItem.product_id, SaleItem.qty, SaleItem.unit_price, SaleItem.line_total]
    can_create = False
    can_edit = False
    can_delete = False        

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