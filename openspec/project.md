# TERRAFOOD · Fuego & Botánica — OpenSpec Project Context

## 1. Visión del Proyecto
**TERRAFOOD · Fuego & Botánica** es una plataforma web Full-Stack para alta gastronomía contemporánea. Permite a los comensales autenticarse, explorar el catálogo curado de **Platos Fuertes** y **Postres de Autor** con fotografía gastronómica de alta resolución y precios transparentes, personalizar su orden y almacenar cada pedido de forma persistente en una base de datos relacional.

## 2. Metodología: Open Spec-Driven Development (SDD)
El proyecto se rige bajo **OpenSpec + OpenAPI 3.1 Contract-First**:
1. **Especificación de Dominio (`openspec/specs/*/spec.md`)**: Define requisitos normativos (`SHALL`/`MUST`) y escenarios verificables (`WHEN` / `THEN`) antes de escribir código.
2. **Contrato de API (`openspec/openapi.yaml`)**: Define esquemas JSON, rutas HTTP, códigos de estado y seguridad Bearer Token.
3. **Implementación Validada (`backend/` & `frontend/`)**: El backend en **FastAPI + Pydantic v2** implementa estrictamente los esquemas del contrato y persiste los datos en **SQLite3** (`aurelia.db`).

## 3. Stack Tecnológico Moderno
- **Especificaciones**: OpenSpec Markdown + OpenAPI 3.1.0
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Uvicorn ASGI
- **Persistencia**: SQLite 3 relacional (`users`, `menu_items`, `orders`, `order_items`)
- **Frontend**: React 18 (ES6+), Tailwind CSS, Lucide Icons, Glassmorphism UI
- **Autenticación**: Token de sesión firmado (SHA-256 + Salt) con soporte para Login, Registro y Cuenta Demo VIP
