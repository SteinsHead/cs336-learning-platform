create table if not exists public.learning_states (
  user_id uuid primary key references auth.users(id) on delete cascade,
  state jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.learning_states enable row level security;

drop policy if exists "Users can read their own learning state" on public.learning_states;
create policy "Users can read their own learning state"
on public.learning_states
for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can insert their own learning state" on public.learning_states;
create policy "Users can insert their own learning state"
on public.learning_states
for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users can update their own learning state" on public.learning_states;
create policy "Users can update their own learning state"
on public.learning_states
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create index if not exists learning_states_updated_at_idx
on public.learning_states (updated_at desc);
