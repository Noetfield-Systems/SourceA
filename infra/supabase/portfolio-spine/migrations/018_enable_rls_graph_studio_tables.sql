-- 018 — Enable RLS on graph studio tables (Supabase Security Advisor rls_disabled_in_public)
-- Project: kazemnezhadsina144-dot's Project (ldfruywifqnfpwsfgmdl)
-- Access model: service_role via Cloudflare workers; anon/authenticated denied.
-- Applied live: 2026-07-28 via Supabase MCP (security alert remediation).

set search_path = public;

do $$
declare
  t text;
  tables text[] := array[
    'graph_node_manifests',
    'graph_blueprints',
    'graph_compiled_plans',
    'graph_runs'
  ];
begin
  foreach t in array tables
  loop
    if to_regclass('public.' || t) is null then
      raise notice 'skip missing table: %', t;
      continue;
    end if;
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on table public.%I from anon, authenticated', t);
    execute format('grant select, insert, update, delete on table public.%I to service_role', t);
    raise notice 'rls enabled: %', t;
  end loop;
end $$;

notify pgrst, 'reload schema';
