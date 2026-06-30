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
- [x] **Despliegue: local con uvicorn**
- [x] **Divisa: configurable desde `/settings` (default MXN)**

---

*Última actualización: 2026-06-30*
