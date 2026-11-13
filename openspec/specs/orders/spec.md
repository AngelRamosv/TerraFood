# Especificación de Dominio: Gestión y Almacenamiento de Pedidos (`orders`)

## Propósito
Almacenar de forma persistente e íntegra cada pedido realizado por un comensal autenticado en la base de datos SQLite (`orders` y `order_items`), calculando subtotales, impuestos/servicio y permitiendo consultar el historial en tiempo real.

## Requisitos

### Requirement: Creación y Persistencia de Pedido
El sistema **SHALL** registrar en la base de datos todo pedido enviado por un usuario autenticado, guardando folio único (ej. `AUR-8492`), modalidad (`mesa`, `para_llevar`, `domicilio`), número de mesa o dirección, notas del chef, desglose de platillos con precio unitario congelado al momento de la compra y monto total.

#### Scenario: Confirmar un pedido con Platos Fuertes y Postres
- **GIVEN** un comensal autenticado con platillos en su comanda
- **WHEN** envía `POST /api/v1/orders` con `items`, `service_type`, `table_or_address` y `notes`
- **THEN** el sistema persiste el registro en las tablas `orders` y `order_items` de SQLite y devuelve `201 Created` con el objeto `OrderResponse` completo y estado `"En preparación en cocina"`.

### Requirement: Historial de Pedidos del Comensal
El sistema **SHALL** permitir al usuario autenticado consultar todos sus pedidos almacenados en la base de datos ordenados del más reciente al más antiguo.

#### Scenario: Consultar pedidos propios
- **GIVEN** un comensal autenticado que ha realizado pedidos
- **WHEN** solicita `GET /api/v1/orders/my`
- **THEN** el sistema responde `200 OK` con la lista de órdenes almacenadas y sus platillos detallados.
