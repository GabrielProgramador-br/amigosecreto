create table if not exists public.participantes (
    email text primary key,
    auth_user_id uuid unique references auth.users(id) on delete cascade,
    nome text not null,
    endereco text not null,
    criado_em timestamptz not null default now()
);

alter table public.participantes
    add column if not exists auth_user_id uuid references auth.users(id) on delete cascade;

create unique index if not exists participantes_auth_user_id_unico
    on public.participantes(auth_user_id)
    where auth_user_id is not null;

create table if not exists public.sugestoes (
    id bigint generated always as identity primary key,
    email text not null references public.participantes(email) on delete cascade,
    data_hora text not null,
    criada_em timestamptz not null default now(),
    constraint sugestoes_email_data_hora_unica unique (email, data_hora)
);

alter table public.participantes enable row level security;
alter table public.sugestoes enable row level security;

revoke all on public.participantes, public.sugestoes from anon, authenticated;
grant select (email, nome, endereco) on public.participantes to authenticated;
grant insert (email, auth_user_id, nome, endereco) on public.participantes to authenticated;
grant update (auth_user_id, nome, endereco) on public.participantes to authenticated;
grant select (email, data_hora) on public.sugestoes to authenticated;
grant insert (email, data_hora) on public.sugestoes to authenticated;
grant usage, select on sequence public.sugestoes_id_seq to authenticated;

grant all privileges on table public.participantes, public.sugestoes to service_role;
grant usage, select on sequence public.sugestoes_id_seq to service_role;

drop policy if exists participantes_ler_proprio on public.participantes;
create policy participantes_ler_proprio
on public.participantes for select to authenticated
using (true);

drop policy if exists participantes_inserir_proprio on public.participantes;
create policy participantes_inserir_proprio
on public.participantes for insert to authenticated
with check (
    lower(email) = lower(auth.jwt() ->> 'email')
    and auth_user_id = auth.uid()
);

drop policy if exists participantes_atualizar_proprio on public.participantes;
create policy participantes_atualizar_proprio
on public.participantes for update to authenticated
using (
    lower(email) = lower(auth.jwt() ->> 'email')
    and (auth_user_id is null or auth_user_id = auth.uid())
)
with check (
    lower(email) = lower(auth.jwt() ->> 'email')
    and auth_user_id = auth.uid()
);

drop policy if exists sugestoes_ler_proprias on public.sugestoes;
create policy sugestoes_ler_proprias
on public.sugestoes for select to authenticated
using (lower(email) = lower(auth.jwt() ->> 'email'));

drop policy if exists sugestoes_inserir_proprias on public.sugestoes;
create policy sugestoes_inserir_proprias
on public.sugestoes for insert to authenticated
with check (lower(email) = lower(auth.jwt() ->> 'email'));

create or replace function public.listar_participantes()
returns table (nome text)
language sql
security definer
set search_path = ''
as $$
    select p.nome
    from public.participantes as p
    order by p.nome;
$$;

revoke all on function public.listar_participantes() from public, anon;
grant execute on function public.listar_participantes() to authenticated;

create or replace function public.ranking_sugestoes()
returns table (data_hora text, votos bigint)
language sql
security definer
set search_path = ''
as $$
    select s.data_hora, count(*)::bigint as votos
    from public.sugestoes as s
    group by s.data_hora
    order by count(*) desc, s.data_hora;
$$;

revoke all on function public.ranking_sugestoes() from public, anon;
grant execute on function public.ranking_sugestoes() to authenticated;

create or replace function public.validar_limite_sugestoes()
returns trigger
language plpgsql
as $$
begin
    perform pg_advisory_xact_lock(hashtextextended(new.email, 0));

    if (
        select count(*)
        from public.sugestoes
        where email = new.email
    ) >= 10 then
        raise exception 'Limite de 10 sugestoes atingido para este e-mail';
    end if;

    return new;
end;
$$;

drop trigger if exists limitar_sugestoes_por_participante on public.sugestoes;

create trigger limitar_sugestoes_por_participante
before insert on public.sugestoes
for each row execute function public.validar_limite_sugestoes();