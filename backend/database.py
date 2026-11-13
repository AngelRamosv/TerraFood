import hashlib
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "terrafood_restaurant.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> str:
    if salt is None:
        salt = secrets.token_hex(8)
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if "$" not in stored_hash:
        return False
    salt, _ = stored_hash.split("$", 1)
    return hash_password(password, salt) == stored_hash


INITIAL_MENU_ITEMS: List[Dict[str, Any]] = [
    # ======================= PLATOS FUERTES =======================
    {
        "name": "Ribeye Wagyu A5 & Mantequilla de Trufa Negra",
        "subtitle": "Corte Japonés · Carbón de Encino · 320g",
        "category": "platos_fuertes",
        "description": (
            "Corte Wagyu A5 sellado a la brasa viva de encino, glaseado con mantequilla "
            "clarificada de trufa negra del Périgord, milhojas de papa trufada y reducción de Oporto 20 años."
        ),
        "price": 68.00,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1000&q=85",
        "badge": "Firma del Chef",
        "prep_time_min": 22,
        "calories": 790,
        "pairing": "Cabernet Sauvignon Reserva · Napa Valley",
        "rating": 4.9,
    },
    {
        "name": "Pulpo a las Brasas en Mole Negro Oaxaqueño",
        "subtitle": "Tentáculo Colosal · Ceniza de Totomoxtle · 260g",
        "category": "platos_fuertes",
        "description": (
            "Pulpo del Pacífico confitado durante 4 horas y terminado al carbón, servido sobre "
            "espejo de mole negro artesanal de 28 ingredientes, puré de plátano macho asado y ajonjolí tostado."
        ),
        "price": 39.50,
        "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=1000&q=85",
        "badge": "Estrella Michelin",
        "prep_time_min": 18,
        "calories": 540,
        "pairing": "Mezcal Tobalá Joven & Vino Blanco Albariño",
        "rating": 4.9,
    },
    {
        "name": "Salmón Salvaje Ora King & Costra de Pistacho",
        "subtitle": "Nueva Zelanda · Velouté de Azafrán · 250g",
        "category": "platos_fuertes",
        "description": (
            "Lomo de salmón Ora King con piel crujiente y costra de pistacho siciliano, acompañado "
            "de espárragos trigueros a la parrilla, emulsión de azafrán español y caviar de trucha."
        ),
        "price": 36.00,
        "image_url": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1000&q=85",
        "badge": "Omega & Botánica",
        "prep_time_min": 16,
        "calories": 580,
        "pairing": "Chardonnay Barrica Francesa · Borgoña",
        "rating": 4.8,
    },
    {
        "name": "Risotto Acquerello de Hongos Silvestres & Oro 24K",
        "subtitle": "Arroz Añejado · Parmigiano Reggiano 36 Meses",
        "category": "platos_fuertes",
        "description": (
            "Arroz Acquerello cremoso mantecado con boletus edulis, colmenillas silvestres, aceite "
            "de trufa blanca de Alba, crujiente de parmesano y lámina comestible de oro de 24 quilates."
        ),
        "price": 34.00,
        "image_url": "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=1000&q=85",
        "badge": "Vegetariano de Lujo",
        "prep_time_min": 20,
        "calories": 640,
        "pairing": "Barolo DOCG · Piamonte",
        "rating": 4.9,
    },
    {
        "name": "Costilla Corta Braseada 36h al Vino Tinto",
        "subtitle": "Short Rib Black Angus · Cremoso de Coliflor Ahumada",
        "category": "platos_fuertes",
        "description": (
            "Short Rib Black Angus cocinado a baja temperatura durante 36 horas en reducción de Malbec "
            "y romero fresco, sobre mousseline sedoso de coliflor rostizada y chalotas caramelizadas."
        ),
        "price": 44.00,
        "image_url": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1000&q=85",
        "badge": "Cocción Lenta 36h",
        "prep_time_min": 15,
        "calories": 820,
        "pairing": "Malbec Gran Reserva · Mendoza",
        "rating": 4.9,
    },
    {
        "name": "Langosta Termidor a la Leña & Brioche Tostado",
        "subtitle": "Cola de Langosta Caribeña · Mantequilla de Estragón",
        "category": "platos_fuertes",
        "description": (
            "Cola de langosta fresca gratinada al horno de piedra con salsa bechamel al Cognac XO, "
            "mostaza Dijon antigua, queso Gruyère de cueva y limón amarillo tatemado."
        ),
        "price": 58.00,
        "image_url": "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=1000&q=85",
        "badge": "Edición Limitada",
        "prep_time_min": 24,
        "calories": 690,
        "pairing": "Champagne Brut Blanc de Blancs",
        "rating": 5.0,
    },
    {
        "name": "Tagliolini Artesanal de Langostinos & Bisque Ahumado",
        "subtitle": "Pasta Fresca al Huevo · Azafrán & Tomate Cherry Confit",
        "category": "platos_fuertes",
        "description": (
            "Pasta fresca estirada a mano con yema de granja, salteada con langostinos tigre a la brasa, "
            "reducción intensa de bisque de crustáceos, albahaca morada y ralladura de limón Amalfi."
        ),
        "price": 32.50,
        "image_url": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=1000&q=85",
        "badge": "Favorito de la Casa",
        "prep_time_min": 16,
        "calories": 610,
        "pairing": "Pinot Grigio · Véneto",
        "rating": 4.8,
    },
    # ======================= POSTRES DE AUTOR =======================
    {
        "name": "Esfera de Chocolate Valrhona 70% & Oro Líquido",
        "subtitle": "Postre Interactivo · Caramelo Salado Caliente",
        "category": "postres",
        "description": (
            "Domo de chocolate oscuro Guanaja 70% que se funde en mesa al verter toffee caliente de "
            "ron añejo, revelando corazón de mousse de avellana del Piamonte y helado de vainilla de Papantla."
        ),
        "price": 19.50,
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1000&q=85",
        "badge": "Icono Terrafood",
        "prep_time_min": 10,
        "calories": 480,
        "pairing": "Espresso Martini o Pedro Ximénez",
        "rating": 5.0,
    },
    {
        "name": "Tarta Vasca Quemada de Pistacho & Frutos del Bosque",
        "subtitle": "Centro Fundente · Pistacho Verde de Bronte",
        "category": "postres",
        "description": (
            "Cheesecake vasco horneado a alta temperatura con corteza caramelizada y centro ultra cremoso "
            "de praliné de pistacho siciliano, acompañado de compota tibia de frambuesas orgánicas."
        ),
        "price": 16.50,
        "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=1000&q=85",
        "badge": "Más Pedido",
        "prep_time_min": 8,
        "calories": 430,
        "pairing": "Vino Sauternes o Matcha Ceremonial",
        "rating": 4.9,
    },
    {
        "name": "Tiramisú Imperial al Amaretto Disaronno",
        "subtitle": "Mascarpone Artesanal · Espresso de Especialidad",
        "category": "postres",
        "description": (
            "Bizcochos savoiardi horneados en casa embebidos en espresso etíope recién extraído y licor "
            "Amaretto, capas aéreas de crema de mascarpone y cacao alcalino holandés."
        ),
        "price": 15.00,
        "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=1000&q=85",
        "badge": "Receta Clásica",
        "prep_time_min": 7,
        "calories": 410,
        "pairing": "Ristretto Doble o Grappa",
        "rating": 4.8,
    },
    {
        "name": "Milhojas Caramelizado de Vainilla Tahití & Yuzu",
        "subtitle": "Hojaldre Invertido · Crema Diplomática & Gel Cítrico",
        "category": "postres",
        "description": (
            "Láminas ultra crujientes de hojaldre francés caramelizado al momento, intercaladas con "
            "crema diplomática de vainilla de Tahití, toques vibrantes de yuzu japonés y flores comestibles."
        ),
        "price": 17.50,
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1000&q=85",
        "badge": "Alta Repostería",
        "prep_time_min": 12,
        "calories": 390,
        "pairing": "Moscato d'Asti",
        "rating": 4.9,
    },
    {
        "name": "Coulant Tibio de Dulce de Leche & Helado de Tonka",
        "subtitle": "Volcán Fundente · Haba Tonka Amazónica & Nuez Pecana",
        "category": "postres",
        "description": (
            "Volcán horneado al momento con interior líquido de dulce de leche artesanal ahumado, "
            "tierra de nuez pecana garrapiñada y quenelle de helado artesanal de haba tonka."
        ),
        "price": 18.00,
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=1000&q=85",
        "badge": "Horneado al Momento",
        "prep_time_min": 14,
        "calories": 510,
        "pairing": "Carajillo Artesanal al Licor 43",
        "rating": 4.9,
    },
]


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'Miembro Terrafood Gold',
            created_at TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subtitle TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('platos_fuertes', 'postres')),
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image_url TEXT NOT NULL,
            badge TEXT NOT NULL,
            prep_time_min INTEGER NOT NULL,
            calories INTEGER NOT NULL,
            pairing TEXT NOT NULL,
            rating REAL NOT NULL DEFAULT 4.9
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            table_or_address TEXT NOT NULL,
            chef_notes TEXT NOT NULL DEFAULT '',
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            tax REAL NOT NULL,
            tip REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'En preparación en cocina',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            dish_name TEXT NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            custom_note TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );
        """
    )

    # Seed Demo VIP user for TERRAFOOD if not exists
    cur.execute("SELECT id FROM users WHERE email = ?", ("vip@terrafood.com",))
    vip_row = cur.fetchone()
    if not vip_row:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            """
            INSERT INTO users (full_name, email, password_hash, tier, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Alejandro Valdés (VIP)",
                "vip@terrafood.com",
                hash_password("Terrafood2026!"),
                "Terrafood Sommelier · Black Tier",
                now_str,
            ),
        )

    # Seed Menu Items if empty
    cur.execute("SELECT COUNT(*) as total FROM menu_items")
    count = cur.fetchone()["total"]
    if count == 0:
        for item in INITIAL_MENU_ITEMS:
            cur.execute(
                """
                INSERT INTO menu_items (
                    name, subtitle, category, description, price,
                    image_url, badge, prep_time_min, calories, pairing, rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["name"],
                    item["subtitle"],
                    item["category"],
                    item["description"],
                    item["price"],
                    item["image_url"],
                    item["badge"],
                    item["prep_time_min"],
                    item["calories"],
                    item["pairing"],
                    item["rating"],
                ),
            )

    conn.commit()
    conn.close()
