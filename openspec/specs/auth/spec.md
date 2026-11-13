# Especificación de Dominio: Autenticación de Comensales (`auth`)

## Propósito
Garantizar que todo acceso al menú interactivo y al registro de pedidos de **TERRAFOOD · Fuego & Botánica** esté asociado a un comensal autenticado.

## Requisitos

### Requirement: Inicio de Sesión de Comensal
El sistema **SHALL** permitir a los usuarios registrados iniciar sesión mediante correo electrónico y contraseña, devolviendo un token de sesión y el perfil del comensal.

#### Scenario: Login exitoso con credenciales válidas
- **GIVEN** un comensal registrado con email `vip@terrafood.com`
- **WHEN** envía `POST /api/v1/auth/login` con su email y contraseña correcta
- **THEN** el sistema responde `200 OK` con `access_token`, `user.id`, `user.full_name`, `user.email` y `user.tier`.

#### Scenario: Credenciales inválidas
- **GIVEN** un intento de acceso con contraseña incorrecta
- **WHEN** envía `POST /api/v1/auth/login`
- **THEN** el sistema responde `401 Unauthorized` con mensaje claro en español.

### Requirement: Registro de Nuevos Comensales
El sistema **SHALL** permitir a nuevos clientes crear una cuenta proporcionando nombre completo, correo electrónico y contraseña de al menos 6 caracteres.

#### Scenario: Registro exitoso
- **GIVEN** un visitante nuevo sin cuenta previa
- **WHEN** envía `POST /api/v1/auth/register` con datos válidos
- **THEN** el sistema almacena el usuario en la tabla `users` y retorna `201 Created` con sesión activa inmediata.
