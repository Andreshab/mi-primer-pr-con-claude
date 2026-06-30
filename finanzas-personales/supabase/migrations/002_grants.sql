-- ============================================================
-- 002_grants.sql
-- Permisos de acceso para roles de Supabase
-- ============================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

GRANT ALL ON TABLE public.settings             TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.categories           TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.transactions         TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.savings_goals        TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.goal_contributions   TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.savings_goals_with_progress TO anon, authenticated, service_role;
