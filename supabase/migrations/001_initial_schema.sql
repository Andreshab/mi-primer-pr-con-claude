-- ============================================================
-- 001_initial_schema.sql
-- Ejecutar en Supabase → SQL Editor
-- ============================================================

-- Extensión para UUIDs
create extension if not exists "pgcrypto";

-- ────────────────────────────────────────
-- SETTINGS
-- ────────────────────────────────────────
create table if not exists settings (
  id         uuid primary key default gen_random_uuid(),
  key        text not null unique,
  value      text not null,
  created_at timestamptz not null default now()
);

insert into settings (key, value) values
  ('currency',        'MXN'),
  ('currency_symbol', '$'),
  ('currency_locale', 'es-MX')
on conflict (key) do nothing;

-- ────────────────────────────────────────
-- CATEGORIES
-- ────────────────────────────────────────
create type transaction_type as enum ('income', 'expense');

create table if not exists categories (
  id         uuid primary key default gen_random_uuid(),
  name       text not null,
  icon       text not null default '📦',
  type       transaction_type not null,
  color      text not null default '#6366f1',
  created_at timestamptz not null default now()
);

-- Categorías por defecto
insert into categories (name, icon, type, color) values
  ('Salario',        '💼', 'income',  '#22c55e'),
  ('Freelance',      '💻', 'income',  '#10b981'),
  ('Inversiones',    '📈', 'income',  '#06b6d4'),
  ('Otros ingresos', '💰', 'income',  '#84cc16'),
  ('Alimentación',   '🛒', 'expense', '#f97316'),
  ('Transporte',     '🚗', 'expense', '#eab308'),
  ('Vivienda',       '🏠', 'expense', '#8b5cf6'),
  ('Salud',          '🏥', 'expense', '#ec4899'),
  ('Entretenimiento','🎬', 'expense', '#f43f5e'),
  ('Ropa',           '👕', 'expense', '#a78bfa'),
  ('Educación',      '📚', 'expense', '#60a5fa'),
  ('Servicios',      '💡', 'expense', '#94a3b8'),
  ('Otros gastos',   '📦', 'expense', '#6b7280');

-- ────────────────────────────────────────
-- TRANSACTIONS
-- ────────────────────────────────────────
create type transaction_source as enum ('manual', 'import');

create table if not exists transactions (
  id          uuid primary key default gen_random_uuid(),
  amount      numeric(12, 2) not null check (amount > 0),
  type        transaction_type not null,
  category_id uuid not null references categories(id),
  description text,
  date        date not null,
  source      transaction_source not null default 'manual',
  created_at  timestamptz not null default now()
);

create index if not exists idx_transactions_date        on transactions(date desc);
create index if not exists idx_transactions_category_id on transactions(category_id);
create index if not exists idx_transactions_type        on transactions(type);

-- ────────────────────────────────────────
-- SAVINGS GOALS
-- ────────────────────────────────────────
create type goal_status as enum ('active', 'completed', 'cancelled');

create table if not exists savings_goals (
  id             uuid primary key default gen_random_uuid(),
  name           text not null,
  target_amount  numeric(12, 2) not null check (target_amount > 0),
  deadline       date,
  status         goal_status not null default 'active',
  created_at     timestamptz not null default now()
);

-- ────────────────────────────────────────
-- GOAL CONTRIBUTIONS
-- ────────────────────────────────────────
create table if not exists goal_contributions (
  id         uuid primary key default gen_random_uuid(),
  goal_id    uuid not null references savings_goals(id) on delete cascade,
  amount     numeric(12, 2) not null check (amount > 0),
  date       date not null,
  note       text,
  created_at timestamptz not null default now()
);

create index if not exists idx_goal_contributions_goal_id on goal_contributions(goal_id);

-- ────────────────────────────────────────
-- VISTA: current_amount por meta (calculado)
-- ────────────────────────────────────────
create or replace view savings_goals_with_progress as
select
  g.*,
  coalesce(sum(c.amount), 0)                        as current_amount,
  round(coalesce(sum(c.amount), 0) / g.target_amount * 100, 1) as progress_pct
from savings_goals g
left join goal_contributions c on c.goal_id = g.id
group by g.id;
