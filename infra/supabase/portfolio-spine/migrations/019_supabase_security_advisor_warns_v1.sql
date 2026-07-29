-- 019 — Supabase Security Advisor WARN remediation (graph studio project)
-- Project: ldfruywifqnfpwsfgmdl
-- Clears: function_search_path_mutable, extension_in_public (vector),
--         rls_policy_always_true (telemetry_logs).

-- 1) Extension in public → extensions schema (Supabase recommended)
create schema if not exists extensions;
grant usage on schema extensions to postgres, anon, authenticated, service_role;
alter extension vector set schema extensions;

-- 2) function_search_path_mutable
create or replace function public.match_documents(
  query_embedding vector,
  match_count integer default 5,
  filter jsonb default '{}'::jsonb
)
returns table(
  id uuid,
  content text,
  memory_type text,
  metadata jsonb,
  similarity double precision,
  created_at timestamp with time zone
)
language sql
stable
set search_path = extensions, public
as $function$
  select
    t.id,
    t.content,
    t.memory_type,
    t.metadata,
    1 - (t.embedding <=> query_embedding) as similarity,
    t.created_at
  from telemetry_logs t
  where t.embedding is not null
    and (
      filter = '{}'::jsonb
      or (filter ? 'memory_type' and t.memory_type = filter->>'memory_type')
    )
  order by t.embedding <=> query_embedding
  limit match_count;
$function$;

create or replace function public.match_telemetry(
  query_embedding vector,
  match_count integer default 5
)
returns table(
  id uuid,
  content text,
  memory_type text,
  metadata jsonb,
  similarity double precision,
  created_at timestamp with time zone
)
language sql
stable
set search_path = extensions, public
as $function$
  select
    t.id,
    t.content,
    t.memory_type,
    t.metadata,
    1 - (t.embedding <=> query_embedding) as similarity,
    t.created_at
  from telemetry_logs t
  where t.embedding is not null
  order by t.embedding <=> query_embedding
  limit match_count;
$function$;

-- 3) telemetry_logs — replace always-true WITH CHECK
drop policy if exists telemetry_anon_insert on public.telemetry_logs;

create policy telemetry_anon_insert_v2
  on public.telemetry_logs
  for insert
  to anon
  with check (
    coalesce(length(trim(content)), 0) > 0
    and coalesce(length(trim(memory_type)), 0) > 0
    and (metadata is null or jsonb_typeof(metadata) = 'object')
  );

comment on policy telemetry_anon_insert_v2 on public.telemetry_logs is
  'Anon telemetry insert with content + memory_type validation (replaces WITH CHECK true).';

notify pgrst, 'reload schema';
