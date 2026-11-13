from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., description="Correo electrónico del comensal")
    password: str = Field(..., min_length=4, description="Contraseña de acceso")


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Nombre completo del comensal")
    email: str = Field(..., description="Correo electrónico único")
    password: str = Field(..., min_length=6, description="Contraseña de al menos 6 caracteres")


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: str
    tier: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserProfile


class MenuItem(BaseModel):
    id: int
    name: str
    subtitle: str
    category: Literal["platos_fuertes", "postres"]
    description: str
    price: float
    image_url: str
    badge: str
    prep_time_min: int
    calories: int
    pairing: str
    rating: float


class OrderItemInput(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=20)
    custom_note: Optional[str] = ""


class OrderCreateRequest(BaseModel):
    service_type: Literal["mesa", "para_llevar", "domicilio"] = "mesa"
    table_or_address: str = Field(..., min_length=1, description="Número de mesa o dirección de entrega")
    chef_notes: Optional[str] = ""
    tip_percentage: float = Field(default=10.0, ge=0.0, le=50.0)
    payment_method: str = Field(default="Tarjeta Signature / Apple Pay")
    items: List[OrderItemInput] = Field(..., min_length=1)


class OrderItemDetail(BaseModel):
    id: int
    menu_item_id: int
    dish_name: str
    category: str
    image_url: str
    quantity: int
    unit_price: float
    line_total: float
    custom_note: str


class OrderResponse(BaseModel):
    id: int
    folio: str
    user_id: int
    customer_name: str
    customer_email: str
    service_type: str
    table_or_address: str
    chef_notes: str
    payment_method: str
    subtotal: float
    tax: float
    tip: float
    total: float
    status: str
    created_at: str
    items: List[OrderItemDetail]
