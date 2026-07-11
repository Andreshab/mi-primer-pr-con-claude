# Spec: Gestor de Finanzas Personales

> Estado: BORRADOR — pendiente de revisión y aprobación antes de escribir código.

---

## 1. Visión general

App web personal para registrar, categorizar y analizar ingresos y gastos, con metas de ahorro y reportes visuales. Usuario único. Backend en Python, base de datos en Supabase (PostgreSQL).

---

## 2. Stack (pendiente de confirmar frontend)

| Capa | Tecnología |
|------|-----------|
| Backend | Python — FastAPI |
| Frontend | HTMX + Jinja2 + TailwindCSS (CDN) |
| Base de datos | Supabase (PostgreSQL) |
| Auth | Supabase Auth (email/password) |
| Reportes | Plotly (charts embebidos en HTML) |
| Importación | Archivos CSV |
| Despliegue | Local (uvicorn) |

---

## 3. Alcance (v1)

### En scope
- [ ] Registro manual de transacciones (ingreso / gasto)
- [ ] Categorías personalizables (crear, editar, eliminar)
- [ ] Importación de transacciones históricas desde CSV
- [ ] Metas de ahorro con seguimiento de progreso
- [ ] Reportes: gastos por categoría, flujo mensual, progreso de metas
- [ ] Dashboard con resumen del mes actual

### Fuera de scope (v1)
- Múltiples usuarios / cuentas compartidas
- Conexión en tiempo real con bancos
- App móvil nativa
- Notificaciones / alertas automáticas
- Exportación de reportes a PDF

---

## 4. Modelos de datos

### `settings`
```
id            uuid  PK
key           text  NOT NULL UNIQUE
value         text  NOT NULL
created_at    timestamp
```
Valores iniciales: `currency` → `"MXN"`, `currency_symbol` → `"$"`, `currency_locale` → `"es-MX"`

### `categories`
```
id            uuid  PK
name          text  NOT NULL
icon          text  (emoji o nombre de icono)
type          enum  ('income' | 'expense')
color         text  (hex color)
created_at    timestamp
```

### `transactions`
```
id            uuid  PK
amount        numeric(12,2)  NOT NULL
type          enum  ('income' | 'expense')
category_id   uuid  FK → categories.id
description   text
date          date  NOT NULL
source        enum  ('manual' | 'import')
created_at    timestamp
```

### `savings_goals`
```
id            uuid  PK
name          text  NOT NULL
target_amount numeric(12,2)  NOT NULL
current_amount numeric(12,2) DEFAULT 0
deadline      date  (nullable)
status        enum  ('active' | 'completed' | 'cancelled')
created_at    timestamp
```

### `goal_contributions`
```
id            uuid  PK
goal_id       uuid  FK → savings_goals.id
amount        numeric(12,2)  NOT NULL
date          date  NOT NULL
note          text
created_at    timestamp
```

---

## 5. Funcionalidades y contratos de API

### 5.1 Transacciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/transactions` | Lista con filtros (mes, categoría, tipo) |
| POST | `/transactions` | Crear transacción manual |
| PUT | `/transactions/{id}` | Editar transacción |
| DELETE | `/transactions/{id}` | Eliminar transacción |
| POST | `/transactions/import` | Importar CSV |

**Filtros GET /transactions:**
- `month` (YYYY-MM)
- `category_id`
- `type` (income/expense)
- `page`, `limit`

**Formato CSV de importación:**
```
date,amount,type,category,description
2024-01-15,1500.00,income,Salario,Pago enero
2024-01-20,250.00,expense,Alimentación,Supermercado
```

### 5.2 Categorías

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/categories` | Lista todas |
| POST | `/categories` | Crear |
| PUT | `/categories/{id}` | Editar |
| DELETE | `/categories/{id}` | Eliminar (solo si sin transacciones) |

### 5.3 Metas de ahorro

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/goals` | Lista todas las metas |
| POST | `/goals` | Crear meta |
| PUT | `/goals/{id}` | Editar meta |
| POST | `/goals/{id}/contribute` | Registrar aporte |
| GET | `/goals/{id}/history` | Historial de aportes |

### 5.5 Configuración

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/settings` | Obtener configuración actual |
| PUT | `/settings` | Actualizar clave(s) de configuración |

Claves soportadas: `currency`, `currency_symbol`, `currency_locale`

### 5.4 Reportes

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/reports/monthly` | Resumen mes: total ingresos, gastos, balance |
| GET | `/reports/by-category` | Gastos agrupados por categoría (período) |
| GET | `/reports/trend` | Flujo mensual de los últimos N meses |
| GET | `/reports/goals` | Progreso de todas las metas activas |

---

## 6. Vistas (páginas)

| Vista | Ruta web | Descripción |
|-------|---------|-------------|
| Dashboard | `/` | Resumen mes actual + accesos rápidos |
| Transacciones | `/transactions` | Lista + formulario + botón importar |
| Categorías | `/categories` | CRUD de categorías |
| Metas | `/goals` | Lista de metas + aportes |
| Reportes | `/reports` | Gráficas interactivas |
| Configuración | `/settings` | Divisa y preferencias |

---

## 7. Reglas de negocio

1. No se puede eliminar una categoría que tenga transacciones asociadas — se debe reasignar primero.
2. El `current_amount` de una meta se calcula sumando sus `goal_contributions` (no se almacena manualmente).
3. Una meta pasa a `completed` automáticamente cuando `current_amount >= target_amount`.
4. En importación CSV, si una categoría no existe, se crea automáticamente.
5. Las transacciones no tienen usuario_id en v1 (single-user), pero el schema debe permitir agregarlo fácilmente en v2.

---

## 8. Estructura de carpetas propuesta

```
finanzas-personales/
├── SPEC.md               ← este archivo
├── backend/
│   ├── main.py
│   ├── database.py       ← cliente Supabase
│   ├── models/           ← Pydantic schemas
│   ├── routers/          ← endpoints por dominio
│   ├── services/         ← lógica de negocio
│   └── requirements.txt
├── frontend/             ← según opción A o B
└── supabase/
    └── migrations/       ← SQL de creación de tablas
```

---

## 9. Decisiones resueltas

- [x] **Frontend: HTMX + Jinja2 + TailwindCSS**
- [x] **Despliegue: local con uvicorn → Render (free tier) + Supabase**
- [x] **Divisa: configurable desde `/settings` (default MXN)**

---

## 10. Etapas de evolución (v1.1)

> Estado: BORRADOR — pendiente de aprobación antes de escribir código.

### Etapa 5 — Presupuestos por categoría de gasto

**Objetivo:** definir un monto de presupuesto mensual por cada categoría de gasto y visualizar cuánto se lleva consumido en el mes.

#### 5.1 Modelo de datos

Nueva tabla `budgets` (migración `003_budgets.sql`):

```
id            uuid  PK
category_id   uuid  FK → categories.id  NOT NULL UNIQUE
amount        numeric(12,2)  NOT NULL  CHECK (amount > 0)
created_at    timestamp
updated_at    timestamp
```

Decisiones de diseño:
- **Un presupuesto por categoría** (UNIQUE en `category_id`), monto fijo que aplica a todos los meses. No hay presupuestos distintos por mes en v1.1 — simplifica el modelo y cubre el caso de uso principal.
- Solo aplica a categorías de tipo `expense`. Se valida en backend.
- El consumo del mes se calcula al vuelo: suma de `transactions` de esa categoría en el mes consultado (no se almacena).

#### 5.2 API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/budgets` | Lista presupuestos con consumo del mes (`?month=YYYY-MM`, default mes actual) |
| PUT | `/api/budgets/{category_id}` | Crear o actualizar (upsert) el presupuesto de una categoría |
| DELETE | `/api/budgets/{category_id}` | Eliminar el presupuesto de una categoría |

Respuesta de GET (por ítem): `category_id`, `category_name`, `category_icon`, `category_color`, `budget_amount`, `spent`, `remaining`, `pct` (0–100+, puede superar 100).

#### 5.3 Vistas / UX

- **Nueva página `/budgets`** ("Presupuestos") en el sidebar, entre Metas y Reportes:
  - Lista todas las categorías de gasto. Cada fila muestra: icono + nombre, input de monto (vacío si no tiene presupuesto), barra de progreso con gasto del mes vs. presupuesto.
  - Guardar/editar el monto vía HTMX (`hx-put`) sin recargar la página; botón para quitar el presupuesto.
  - Selector de mes para consultar consumo de meses anteriores (el presupuesto es el mismo, cambia el gasto).
  - Código de color de la barra: verde < 80 %, ámbar 80–100 %, rojo > 100 %.
- **Dashboard:** nueva tarjeta "Presupuesto del mes" con el total presupuestado vs. gastado en categorías presupuestadas, y las categorías excedidas destacadas en rojo. Se refresca con el evento `transactionCreated` existente.

#### 5.4 Reglas de negocio

1. Solo las categorías `expense` pueden tener presupuesto (400 si se intenta con una de ingreso).
2. `amount` debe ser > 0; para "quitar" un presupuesto se usa DELETE, no monto 0.
3. Al eliminar una categoría se elimina su presupuesto (ON DELETE CASCADE) — la regla existente de no borrar categorías con transacciones sigue aplicando.
4. El excedente (> 100 %) se muestra, nunca se bloquea el registro de transacciones.

#### 5.5 Criterios de aceptación

- [ ] Puedo asignar $X a una categoría de gasto y ver la barra reflejar el gasto del mes actual.
- [ ] Editar el monto actualiza la barra sin recargar la página.
- [ ] Registrar una transacción desde el modal global actualiza la tarjeta de presupuesto del dashboard.
- [ ] Una categoría de ingreso no aparece en `/budgets`.

---

### Etapa 6 — Edición y control de metas de ahorro

**Objetivo:** poder editar una meta existente (nombre, monto objetivo, fecha límite) y controlar su ciclo de vida (cancelar, reactivar, eliminar).

#### 6.1 Modelo de datos

Sin cambios de schema — `savings_goals` ya soporta todo (el endpoint `PUT /api/goals/{id}` y el modelo `GoalUpdate` ya existen en backend; falta exponerlo en la UI y completar el ciclo de vida).

#### 6.2 API

| Método | Ruta | Descripción |
|--------|------|-------------|
| PUT | `/api/goals/{id}` | Ya existe — editar nombre, target, deadline, status |
| DELETE | `/api/goals/{id}` | **Nuevo** — eliminar meta y sus aportes (cascade) |
| PUT | `/partials/goals/{id}` | **Nuevo** — editar vía HTMX, devuelve la card actualizada |
| DELETE | `/partials/goals/{id}` | **Nuevo** — eliminar vía HTMX, devuelve vacío |

#### 6.3 Vistas / UX

En cada `goal_card`:
- Botón de menú (⋯ o ✏️) que despliega el formulario de edición inline (mismo patrón `<details>` que "+ Agregar aporte"): nombre, monto objetivo, fecha límite.
- Acciones según estado:
  - `active` → **Cancelar** (pasa a `cancelled`)
  - `cancelled` → **Reactivar** (pasa a `active`) y **Eliminar** (con `hx-confirm`)
  - `completed` → solo lectura (editar target puede reabrirla, ver regla 3)
- Al guardar, la card se reemplaza vía `hx-swap="outerHTML"` (patrón ya usado en aportes).

#### 6.4 Reglas de negocio

1. Editar `target_amount` recalcula el estado: si `current_amount >= nuevo target` → `completed`; si una meta `completed` sube su target por encima de lo aportado → vuelve a `active`.
2. `target_amount` editado debe ser > 0.
3. Eliminar una meta borra sus `goal_contributions` (ON DELETE CASCADE — verificar que la FK ya lo tenga; si no, migración `004`).
4. Los aportes históricos nunca se editan desde la meta (fuera de scope).

#### 6.5 Criterios de aceptación

- [ ] Puedo renombrar una meta y cambiar su monto objetivo desde la card.
- [ ] Si bajo el target por debajo de lo aportado, la meta pasa a "Completada" automáticamente.
- [ ] Puedo cancelar una meta activa y reactivarla después.
- [ ] Puedo eliminar una meta cancelada, con confirmación previa.

---

### Orden de ejecución

1. **Etapa 5** — presupuestos (migración + backend + UI + dashboard).
2. **Etapa 6** — edición de metas (backend + UI, sin migración salvo verificación del CASCADE).

Cada etapa se implementa, se verifica en local y se despliega antes de iniciar la siguiente.

---

*Última actualización: 2026-07-03*
