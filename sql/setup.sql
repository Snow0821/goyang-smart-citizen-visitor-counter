create table if not exists public.page_views (
  page_key text primary key,
  view_count bigint not null default 0 check (view_count >= 0),
  updated_at timestamptz not null default now()
);

alter table public.page_views enable row level security;

revoke all on table public.page_views from anon, authenticated;

create or replace function public.increment_page_view(target_key text)
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  new_count bigint;
begin
  insert into public.page_views (page_key, view_count)
  values (target_key, 1)
  on conflict (page_key)
  do update
    set view_count = public.page_views.view_count + 1,
        updated_at = now()
  returning view_count into new_count;

  return new_count;
end;
$$;

revoke all on function public.increment_page_view(text) from public;
revoke all on function public.increment_page_view(text) from anon, authenticated;
grant execute on function public.increment_page_view(text) to service_role;
