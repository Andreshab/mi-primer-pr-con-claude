-- ============================================================
-- 003_budgets.sql
-- Presupuestos mensuales por categoría de gasto (Etapa 5)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.budgets (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id   uuid NOT NULL UNIQUE REFERENCES public.categories(id) ON DELETE CASCADE,
    amount        numeric(12,2) NOT NULL CHECK (amount > 0),
    created_at    timestamptz DEFAULT now(),
    updated_at    timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_budgets_category ON public.budgets(category_id);

GRANT ALL ON TABLE public.budgets TO anon, authenticated, service_role;
