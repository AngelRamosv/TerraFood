import random
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.database import (
    BASE_DIR,
    DB_PATH,
    get_connection,
    hash_password,
    init_db,
    verify_password,
)
from backend.schemas import (
    AuthResponse,
    LoginRequest,
    MenuItem,
    OrderCreateRequest,
    OrderItemDetail,
    OrderResponse,
    RegisterRequest,
    UserProfile,
)

app = FastAPI(
    title="TERRAFOOD · Fuego & Botánica — OpenSpec API",
    version="1.0.0",
    description=(
        "API Full-Stack desarrollada bajo metodología Open Spec-Driven Development (SDD) "
        "para el restaurante de alta gastronomía TERRAFOOD · Fuego & Botánica."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def create_session_token(conn, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user_id, now_str),
    )
    conn.commit()
    return token


def get_current_user(authorization: Optional[str] = Header(default=None)) -> UserProfile:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión para realizar esta operación.",
        )
    token = authorization.split(" ", 1)[1].strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT u.id, u.full_name, u.email, u.tier, u.created_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ?
        """,
        (token,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada. Por favor inicia sesión nuevamente.",
        )
    return UserProfile(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        tier=row["tier"],
        created_at=row["created_at"],
    )


@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["Auth"])
def login(payload: LoginRequest) -> AuthResponse:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, full_name, email, password_hash, tier, created_at FROM users WHERE LOWER(email) = LOWER(?)",
        (payload.email.strip(),),
    )
    row = cur.fetchone()
    if not row or not verify_password(payload.password, row["password_hash"]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos.",
        )

    token = create_session_token(conn, row["id"])
    conn.close()
    return AuthResponse(
        access_token=token,
        user=UserProfile(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            tier=row["tier"],
            created_at=row["created_at"],
        ),
    )


@app.post(
    "/api/v1/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
def register(payload: RegisterRequest) -> AuthResponse:
    conn = get_connection()
    cur = conn.cursor()
    email_clean = payload.email.strip().lower()
    cur.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta registrada con este correo electrónico.",
        )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pw_hash = hash_password(payload.password)
    tier = "Miembro Terrafood Gold"
    cur.execute(
        """
        INSERT INTO users (full_name, email, password_hash, tier, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (payload.full_name.strip(), email_clean, pw_hash, tier, now_str),
    )
    user_id = cur.lastrowid
    token = create_session_token(conn, user_id)
    conn.close()

    return AuthResponse(
        access_token=token,
        user=UserProfile(
            id=user_id,
            full_name=payload.full_name.strip(),
            email=email_clean,
            tier=tier,
            created_at=now_str,
        ),
    )


@app.get("/api/v1/auth/me", response_model=UserProfile, tags=["Auth"])
def get_me(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    return current_user


@app.get("/api/v1/menu", response_model=List[MenuItem], tags=["Menu"])
def list_menu(
    category: Optional[str] = Query(
        default=None,
        description="Filtrar por categoría: 'platos_fuertes' o 'postres'",
    )
) -> List[MenuItem]:
    conn = get_connection()
    cur = conn.cursor()
    if category in ("platos_fuertes", "postres"):
        cur.execute(
            "SELECT * FROM menu_items WHERE category = ? ORDER BY id ASC",
            (category,),
        )
    else:
        cur.execute("SELECT * FROM menu_items ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [MenuItem(**dict(r)) for r in rows]


def _build_order_response(conn, order_row) -> OrderResponse:
    cur = conn.cursor()
    cur.execute(
        "SELECT full_name, email FROM users WHERE id = ?",
        (order_row["user_id"],),
    )
    u_row = cur.fetchone()
    cur.execute(
        """
        SELECT id, menu_item_id, dish_name, category, image_url,
               quantity, unit_price, line_total, custom_note
        FROM order_items
        WHERE order_id = ?
        ORDER BY id ASC
        """,
        (order_row["id"],),
    )
    items_rows = cur.fetchall()
    items = [OrderItemDetail(**dict(ir)) for ir in items_rows]
    return OrderResponse(
        id=order_row["id"],
        folio=order_row["folio"],
        user_id=order_row["user_id"],
        customer_name=u_row["full_name"] if u_row else "Comensal",
        customer_email=u_row["email"] if u_row else "",
        service_type=order_row["service_type"],
        table_or_address=order_row["table_or_address"],
        chef_notes=order_row["chef_notes"],
        payment_method=order_row["payment_method"],
        subtotal=order_row["subtotal"],
        tax=order_row["tax"],
        tip=order_row["tip"],
        total=order_row["total"],
        status=order_row["status"],
        created_at=order_row["created_at"],
        items=items,
    )


@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],
)
def create_order(
    payload: OrderCreateRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> OrderResponse:
    conn = get_connection()
    cur = conn.cursor()

    resolved_items = []
    subtotal = 0.0

    for item_in in payload.items:
        cur.execute(
            "SELECT id, name, category, price, image_url FROM menu_items WHERE id = ?",
            (item_in.menu_item_id,),
        )
        m_row = cur.fetchone()
        if not m_row:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El platillo con ID {item_in.menu_item_id} no existe en el menú.",
            )
        unit_price = float(m_row["price"])
        line_total = round(unit_price * item_in.quantity, 2)
        subtotal = round(subtotal + line_total, 2)
        resolved_items.append(
            {
                "menu_item_id": m_row["id"],
                "dish_name": m_row["name"],
                "category": m_row["category"],
                "image_url": m_row["image_url"],
                "quantity": item_in.quantity,
                "unit_price": unit_price,
                "line_total": line_total,
                "custom_note": (item_in.custom_note or "").strip(),
            }
        )

    tax = round(subtotal * 0.16, 2)
    tip = round(subtotal * (payload.tip_percentage / 100.0), 2)
    total = round(subtotal + tax + tip, 2)

    folio = f"TF-{random.randint(1000, 9999)}-{datetime.now().strftime('%H%M')}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        """
        INSERT INTO orders (
            folio, user_id, service_type, table_or_address, chef_notes,
            payment_method, subtotal, tax, tip, total, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            folio,
            current_user.id,
            payload.service_type,
            payload.table_or_address.strip(),
            (payload.chef_notes or "").strip(),
            payload.payment_method,
            subtotal,
            tax,
            tip,
            total,
            "En preparación en cocina",
            now_str,
        ),
    )
    order_id = cur.lastrowid

    for r_item in resolved_items:
        cur.execute(
            """
            INSERT INTO order_items (
                order_id, menu_item_id, dish_name, category, image_url,
                quantity, unit_price, line_total, custom_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                r_item["menu_item_id"],
                r_item["dish_name"],
                r_item["category"],
                r_item["image_url"],
                r_item["quantity"],
                r_item["unit_price"],
                r_item["line_total"],
                r_item["custom_note"],
            ),
        )

    conn.commit()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order_row = cur.fetchone()
    response = _build_order_response(conn, order_row)
    conn.close()
    return response


@app.get("/api/v1/orders/my", response_model=List[OrderResponse], tags=["Orders"])
def list_my_orders(
    current_user: UserProfile = Depends(get_current_user),
) -> List[OrderResponse]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
        (current_user.id,),
    )
    rows = cur.fetchall()
    result = [_build_order_response(conn, r) for r in rows]
    conn.close()
    return result


@app.patch("/api/v1/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(
    order_id: int,
    new_status: str = Query(..., description="Nuevo estado del pedido"),
    current_user: UserProfile = Depends(get_current_user),
) -> OrderResponse:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, current_user.id),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    updated_row = cur.fetchone()
    resp = _build_order_response(conn, updated_row)
    conn.close()
    return resp


@app.get("/api/v1/openspec", tags=["OpenSpec"])
def get_openspec_overview():
    """Devuelve artefactos de especificación OpenSpec y métricas en vivo de la base de datos SQLite."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM users")
    users_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM menu_items WHERE category = 'platos_fuertes'")
    mains_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM menu_items WHERE category = 'postres'")
    desserts_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM orders")
    orders_count = cur.fetchone()["c"]
    cur.execute("SELECT COALESCE(SUM(total), 0) as rev FROM orders")
    revenue = round(float(cur.fetchone()["rev"]), 2)
    conn.close()

    openapi_yaml = (BASE_DIR / "openspec" / "openapi.yaml").read_text(encoding="utf-8")
    project_md = (BASE_DIR / "openspec" / "project.md").read_text(encoding="utf-8")
    orders_spec = (BASE_DIR / "openspec" / "specs" / "orders" / "spec.md").read_text(encoding="utf-8")

    return {
        "methodology": "Open Spec-Driven Development (OpenSpec + OpenAPI 3.1.0)",
        "database_file": str(DB_PATH.name),
        "metrics": {
            "registered_users": users_count,
            "platos_fuertes_count": mains_count,
            "postres_count": desserts_count,
            "stored_orders": orders_count,
            "total_revenue_usd": revenue,
        },
        "artifacts": {
            "project_md": project_md,
            "orders_spec_md": orders_spec,
            "openapi_yaml": openapi_yaml,
        },
    }


FRONTEND_HTML = BASE_DIR / "frontend" / "index.html"


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_spa():
    if FRONTEND_HTML.exists():
        return FileResponse(str(FRONTEND_HTML))
    return HTMLResponse("<h1>Frontend en construcción...</h1>")
