# Especificación de Dominio: Catálogo Gastronómico (`menu`)

## Propósito
Presentar el menú de alta cocina dividido en **Platos Fuertes** (`platos_fuertes`) y **Postres de Autor** (`postres`), con fotografías gastronómicas reales, precios curados, tiempo de preparación e insignias del Chef.

## Requisitos

### Requirement: Consulta de Menú por Categoría
El sistema **SHALL** exponer el catálogo completo de platillos o filtrado por categoría (`platos_fuertes`, `postres`), incluyendo imagen de alta resolución, descripción sensorial, precio en USD, calorías, tiempo de preparación e insignia destacada.

#### Scenario: Listar Platos Fuertes y Postres
- **GIVEN** un comensal en la aplicación
- **WHEN** solicita `GET /api/v1/menu`
- **THEN** el sistema responde `200 OK` con la lista completa de platillos disponibles ordenados por categoría y relevancia.

#### Scenario: Filtrar únicamente Postres de Autor
- **GIVEN** el comensal selecciona la pestaña "Postres de Autor"
- **WHEN** solicita `GET /api/v1/menu?category=postres`
- **THEN** el sistema retorna únicamente los platillos con `category == "postres"`.
