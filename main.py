import datetime
import hmac
import secrets
from collections import Counter
from urllib.parse import urlencode

import requests
import streamlit as st
from streamlit_cookies_controller import CookieController

COOKIE_SESSAO = "amigo_secreto_refresh_token"
COOKIE_SESSAO_DURACAO = 30 * 24 * 60 * 60

st.set_page_config(
    page_title="Amigo Secreto | Especial de Natal",
    page_icon="🎁",
    layout="centered",
)

st.markdown("""
    <style>
    :root {
        --pine: #145238;
        --pine-dark: #0c3928;
        --berry: #a9363d;
        --gold: #e7bd72;
        --ink: #263b32;
        --muted: #6f7e75;
        --surface: rgba(255, 255, 255, 0.88);
    }

    .stApp {
        color: var(--ink);
        background:
            radial-gradient(ellipse at 8% 2%, rgba(231, 189, 114, 0.16), transparent 28rem),
            radial-gradient(ellipse at 96% 18%, rgba(20, 82, 56, 0.09), transparent 30rem),
            #f7f6f0;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 880px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 {
        color: var(--pine);
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        letter-spacing: -0.025em;
    }
    h2 { margin-top: 0.4rem; }
    p, label, [data-testid="stMarkdownContainer"] {
        color: var(--ink);
    }

    .holiday-hero {
        position: relative;
        overflow: hidden;
        margin: 0.25rem 0 1.5rem;
        padding: 2.35rem 2.5rem 2.15rem;
        border: 1px solid rgba(231, 189, 114, 0.65);
        border-bottom: 4px solid var(--gold);
        border-radius: 24px;
        color: #fff;
        background:
            radial-gradient(circle at 88% 18%, rgba(231, 189, 114, 0.22), transparent 9rem),
            linear-gradient(132deg, var(--pine-dark), #1a6845 72%, #24714c);
        box-shadow: 0 18px 42px rgba(20, 58, 39, 0.15);
    }
    .holiday-hero::after {
        position: absolute;
        right: 1.35rem;
        bottom: -1.7rem;
        color: rgba(255, 255, 255, 0.12);
        content: "❄";
        font-size: 8rem;
        line-height: 1;
        pointer-events: none;
    }
    .holiday-hero .hero-kicker {
        margin: 0 0 0.65rem;
        color: #f2d89e;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .holiday-hero h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        color: #fff;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        font-size: clamp(2rem, 5vw, 3.1rem);
        font-weight: 700;
        letter-spacing: -0.045em;
        line-height: 1.1;
    }
    .holiday-hero .hero-subtitle {
        position: relative;
        z-index: 1;
        max-width: 34rem;
        margin: 0.8rem 0 0;
        color: rgba(255, 255, 255, 0.83);
        font-size: 1rem;
        line-height: 1.65;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--muted);
        font-size: 0.88rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.4rem;
        padding: 0.4rem;
        border: 1px solid #e8e8df;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.72);
    }
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        min-height: 2.8rem;
        border-radius: 11px;
        color: #64746a;
        font-weight: 600;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color: #fff;
        background: var(--pine);
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: var(--gold);
    }
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        padding: 1.35rem 0.15rem 0;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        min-height: 2.8rem;
        border: 1px solid var(--berry);
        border-radius: 11px;
        color: #fff;
        background: linear-gradient(135deg, #b84648, var(--berry));
        font-weight: 700;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        border-color: #852d34;
        color: #fff;
        background: #922f37;
        box-shadow: 0 6px 16px rgba(169, 54, 61, 0.2);
        transform: translateY(-1px);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-baseweb="select"] > div {
        border-color: #dfe4dc;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.92);
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--pine);
        box-shadow: 0 0 0 1px var(--pine);
    }
    [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid #e5e5dc;
        border-radius: 14px;
        background: var(--surface);
    }
    [data-testid="stAlert"] { border-radius: 12px; }
    hr { border-color: #e5e5dc; }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1rem 1rem 3rem;
        }
        .holiday-hero {
            padding: 1.8rem 1.4rem;
            border-radius: 19px;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 0.1rem; }
        [data-testid="stTabs"] button[data-baseweb="tab"] {
            padding: 0.45rem 0.55rem;
            font-size: 0.82rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


def render_hero():
    st.markdown("""
        <section class="holiday-hero">
            <p class="hero-kicker">✦ Um encontro especial ✦</p>
            <h1>Amigo Secreto</h1>
            <p class="hero-subtitle">
                Presentes, boas conversas e momentos para guardar.
                Vamos preparar nossa celebração?
            </p>
        </section>
    """, unsafe_allow_html=True)


def carregar_configuracao():
    chaves = {
        "url": "SUPABASE_URL",
        "anon_key": "SUPABASE_ANON_KEY",
        "service_key": "SUPABASE_SERVICE_ROLE_KEY",
        "senha_organizador": "INVITE_ADMIN_PASSWORD",
        "app_url": "APP_URL",
    }
    try:
        configuracao = {nome: st.secrets[chave] for nome, chave in chaves.items()}
        configuracao["url"] = configuracao["url"].rstrip("/")
        configuracao["app_url"] = configuracao["app_url"].rstrip("/")
        return configuracao if all(configuracao.values()) else None
    except Exception:
        return None


def requisicao_supabase(configuracao, caminho, metodo="GET", token=None, dados=None, params=None,
                        admin=False, preferencias=None):
    chave = configuracao["service_key"] if admin else configuracao["anon_key"]
    bearer = token or chave
    cabecalhos = {
        "apikey": chave,
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    if preferencias:
        cabecalhos["Prefer"] = preferencias

    resposta = requests.request(
        metodo,
        f"{configuracao['url']}/{caminho.lstrip('/')}",
        headers=cabecalhos,
        params=params,
        json=dados,
        timeout=20,
    )
    resposta.raise_for_status()
    return resposta.json() if resposta.content else None


def salvar_refresh_token(configuracao, cookies, sessao):
    cookies.set(
        COOKIE_SESSAO,
        sessao["refresh_token"],
        path="/",
        expires=datetime.datetime.now() + datetime.timedelta(days=30),
        max_age=COOKIE_SESSAO_DURACAO,
        secure=configuracao["app_url"].startswith("https://"),
        same_site="lax",
    )


def limpar_sessao(configuracao, cookies):
    st.session_state.pop("sessao_supabase", None)
    st.session_state.pop("gerente_autenticado", None)
    if cookies.get(COOKIE_SESSAO) is not None:
        cookies.remove(
            COOKIE_SESSAO,
            path="/",
            secure=configuracao["app_url"].startswith("https://"),
            same_site="lax",
        )


def renovar_sessao(configuracao, cookies, refresh_token):
    sessao = requisicao_supabase(
        configuracao,
        "/auth/v1/token",
        metodo="POST",
        token=configuracao["anon_key"],
        params={"grant_type": "refresh_token"},
        dados={"refresh_token": refresh_token},
    )
    st.session_state.sessao_supabase = sessao
    salvar_refresh_token(configuracao, cookies, sessao)
    return sessao


def validar_sessao(configuracao, cookies):
    sessao = st.session_state.get("sessao_supabase")
    if not sessao:
        refresh_token = cookies.get(COOKIE_SESSAO)
        if not refresh_token:
            return None
        sessao = renovar_sessao(configuracao, cookies, refresh_token)

    try:
        usuario = requisicao_supabase(
            configuracao, "/auth/v1/user", token=sessao["access_token"]
        )
    except requests.HTTPError as erro:
        if erro.response is None or erro.response.status_code != 401:
            raise
        sessao = renovar_sessao(configuracao, cookies, sessao["refresh_token"])
        usuario = requisicao_supabase(
            configuracao, "/auth/v1/user", token=sessao["access_token"]
        )
    sessao["user"] = usuario
    st.session_state.sessao_supabase = sessao
    salvar_refresh_token(configuracao, cookies, sessao)
    return usuario


def confirmar_link(configuracao, cookies):
    token_hash = st.query_params.get("token_hash")
    tipo = st.query_params.get("type")
    if not token_hash or tipo not in {"invite", "email", "magiclink", "recovery"}:
        return False

    render_hero()
    st.subheader("Confirmar seu acesso")
    st.write("Confirme para ativar o link individual compartilhado pelo gerente.")
    if st.button("Confirmar e entrar"):
        try:
            sessao = requisicao_supabase(
                configuracao,
                "/auth/v1/verify",
                metodo="POST",
                token=configuracao["anon_key"],
                dados={"token_hash": token_hash, "type": tipo},
            )
            st.session_state.sessao_supabase = sessao
            salvar_refresh_token(configuracao, cookies, sessao)
            if tipo in {"invite", "recovery"}:
                st.session_state["exigir_nova_senha"] = True
            st.query_params.clear()
            st.rerun()
        except requests.RequestException:
            st.error("Este link expirou ou já foi usado. Peça outro link ao organizador.")
    if not token_hash:
        return False
    return True


def tela_entrada(configuracao, cookies):
    if confirmar_link(configuracao, cookies):
        return

    render_hero()
    st.subheader("Entrar na celebração")
    st.write("Use o e-mail e a senha definidos ao aceitar seu convite.")
    with st.form("formulario_login"):
        email = st.text_input("E-mail").strip().lower()
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if not email or not senha:
            st.warning("Informe seu e-mail e sua senha.")
        else:
            try:
                sessao = requisicao_supabase(
                    configuracao,
                    "/auth/v1/token",
                    metodo="POST",
                    token=configuracao["anon_key"],
                    params={"grant_type": "password"},
                    dados={"email": email, "password": senha},
                )
                st.session_state.sessao_supabase = sessao
                salvar_refresh_token(configuracao, cookies, sessao)
                st.rerun()
            except requests.HTTPError as erro:
                if erro.response is not None and erro.response.status_code in {400, 401}:
                    st.error("E-mail ou senha inválidos.")
                else:
                    st.error("Não foi possível entrar. Tente novamente.")
            except requests.RequestException:
                st.error("Não foi possível conectar ao serviço de autenticação.")

    st.caption("Ainda não tem senha ou precisa redefini-la? Peça um link ao gerente.")
    st.page_link(pagina_configuracao, label="Acesso do gerente", icon="⚙️")


def gerar_link_senha(configuracao, email):
    resultado = requisicao_supabase(
        configuracao,
        "/auth/v1/admin/generate_link",
        metodo="POST",
        admin=True,
        dados={"type": "recovery", "email": email},
    )
    propriedades = resultado.get("properties", resultado)
    token_hash = propriedades.get("hashed_token")
    tipo_verificacao = propriedades.get("verification_type", "recovery")
    if not token_hash:
        raise ValueError("O Supabase não retornou o token do link de redefinição.")

    query = urlencode({"token_hash": token_hash, "type": tipo_verificacao})
    return f"{configuracao['app_url']}/?{query}"


def localizar_usuario_supabase(configuracao, email):
    pagina = 1
    while True:
        resultado = requisicao_supabase(
            configuracao,
            "/auth/v1/admin/users",
            admin=True,
            params={"page": pagina, "per_page": 1000},
        )
        usuarios = resultado.get("users")
        if not isinstance(usuarios, list):
            raise ValueError("O Supabase retornou uma lista de usuários inválida.")
        for usuario in usuarios:
            if (usuario.get("email") or "").lower() == email.lower():
                return usuario.get("id")
        if len(usuarios) < 1000:
            return None
        pagina += 1


def tela_definir_senha(configuracao):
    render_hero()
    st.subheader("Defina sua senha")
    st.write("Crie uma senha para entrar nas próximas vezes com seu e-mail.")
    with st.form("formulario_definir_senha"):
        senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirme a nova senha", type="password")
        salvar = st.form_submit_button("Salvar senha")

    if salvar:
        if not senha:
            st.warning("Informe uma senha.")
        elif senha != confirmar_senha:
            st.error("As senhas não conferem.")
        else:
            try:
                requisicao_supabase(
                    configuracao,
                    "/auth/v1/user",
                    metodo="PUT",
                    token=st.session_state.sessao_supabase["access_token"],
                    dados={"password": senha},
                )
                st.session_state.pop("exigir_nova_senha", None)
                st.session_state["senha_atualizada"] = True
                st.rerun()
            except requests.RequestException:
                st.error("Não foi possível salvar a senha. Confira os requisitos e tente novamente.")


def tela_configuracao():
    configuracao = carregar_configuracao()
    if configuracao is None:
        st.error(
            "Configure SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, "
            "INVITE_ADMIN_PASSWORD e APP_URL nos Secrets do Streamlit."
        )
        st.stop()

    render_hero()
    st.subheader("⚙️ Gerenciamento do gerente")
    if not st.session_state.get("gerente_autenticado"):
        with st.form("formulario_login_gerente"):
            senha = st.text_input("Senha do gerente", type="password")
            entrar = st.form_submit_button("Acessar gerenciamento")
        if entrar:
            if hmac.compare_digest(senha, configuracao["senha_organizador"]):
                st.session_state["gerente_autenticado"] = True
                st.rerun()
            st.error("Senha do gerente incorreta.")
        st.caption("Esta área é restrita ao gerente do grupo.")
        return

    if st.button("Sair do gerenciamento"):
        st.session_state.pop("gerente_autenticado", None)
        st.rerun()

    st.write(
        "Cadastre participantes com nome e e-mail. Cada pessoa informa o próprio endereço "
        "ao entrar pela primeira vez."
    )
    with st.expander("➕ Cadastrar participante", expanded=True):
        with st.form("formulario_novo_participante"):
            novo_nome = st.text_input("Nome do participante")
            novo_email = st.text_input("E-mail do participante").strip().lower()
            cadastrar = st.form_submit_button("Cadastrar e gerar link de senha")

        if cadastrar:
            if not novo_nome.strip() or not novo_email:
                st.warning("Preencha nome e e-mail.")
            else:
                usuario_criado = None
                try:
                    usuario_criado = requisicao_supabase(
                        configuracao,
                        "/auth/v1/admin/users",
                        metodo="POST",
                        admin=True,
                        dados={
                            "email": novo_email,
                            "password": secrets.token_urlsafe(32),
                            "email_confirm": True,
                        },
                    )
                    requisicao_supabase(
                        configuracao,
                        "/rest/v1/participantes",
                        metodo="POST",
                        admin=True,
                        dados={
                            "email": novo_email,
                            "auth_user_id": usuario_criado["id"],
                            "nome": novo_nome.strip(),
                            "endereco": "",
                        },
                        preferencias="return=minimal",
                    )
                    link = gerar_link_senha(configuracao, novo_email)
                    st.success("Participante cadastrado. Compartilhe o link somente com essa pessoa.")
                    st.code(link, language=None)
                    st.warning("O link é individual, secreto e pode ser usado uma única vez.")
                except requests.HTTPError as erro:
                    if usuario_criado and usuario_criado.get("id"):
                        try:
                            requisicao_supabase(
                                configuracao,
                                f"/auth/v1/admin/users/{usuario_criado['id']}",
                                metodo="DELETE",
                                admin=True,
                            )
                        except requests.RequestException:
                            st.error(
                                "O cadastro falhou e a conta criada não pôde ser removida automaticamente. "
                                "Verifique a conta no Supabase antes de tentar novamente."
                            )
                            st.stop()
                    if erro.response is not None and erro.response.status_code == 422:
                        st.error("Esse e-mail já possui uma conta. Use a lista abaixo para gerar um link de senha.")
                    else:
                        st.error("Não foi possível cadastrar o participante no Supabase.")
                except (requests.RequestException, KeyError, ValueError):
                    if usuario_criado and usuario_criado.get("id"):
                        try:
                            requisicao_supabase(
                                configuracao,
                                f"/auth/v1/admin/users/{usuario_criado['id']}",
                                metodo="DELETE",
                                admin=True,
                            )
                        except requests.RequestException:
                            st.error(
                                "O cadastro falhou e a conta criada não pôde ser removida automaticamente. "
                                "Verifique a conta no Supabase antes de tentar novamente."
                            )
                            st.stop()
                    st.error(
                        "A conta não foi cadastrada por completo. Confira a configuração do Supabase e tente novamente."
                    )

    try:
        participantes = requisicao_supabase(
            configuracao,
            "/rest/v1/participantes",
            admin=True,
            params={"select": "email,auth_user_id,nome,endereco", "order": "nome.asc"},
        )
    except requests.RequestException:
        st.error("Não foi possível carregar os participantes.")
        st.stop()

    st.subheader(f"Participantes cadastrados · {len(participantes)}")
    if not participantes:
        st.info("Ainda não há participantes cadastrados.")
        return

    email_remocao_pendente = st.session_state.get("email_remocao_pendente")
    if email_remocao_pendente:
        st.warning(
            f"Remover {email_remocao_pendente}? A conta, o cadastro e as sugestões associadas serão excluídos."
        )
        confirmar_col, cancelar_col = st.columns(2)
        with confirmar_col:
            if st.button("Confirmar remoção", type="primary"):
                participante = next(
                    (p for p in participantes if p["email"] == email_remocao_pendente),
                    None,
                )
                if participante:
                    try:
                        auth_user_id = participante["auth_user_id"] or localizar_usuario_supabase(
                            configuracao, participante["email"]
                        )
                        if auth_user_id:
                            requisicao_supabase(
                                configuracao,
                                f"/auth/v1/admin/users/{auth_user_id}",
                                metodo="DELETE",
                                admin=True,
                            )
                        else:
                            requisicao_supabase(
                                configuracao,
                                "/rest/v1/participantes",
                                metodo="DELETE",
                                admin=True,
                                params={"email": f"eq.{email_remocao_pendente}"},
                            )
                        st.session_state.pop("email_remocao_pendente", None)
                        st.success("Participante removido.")
                        st.rerun()
                    except (requests.RequestException, ValueError):
                        st.error("Não foi possível remover o participante.")
        with cancelar_col:
            if st.button("Cancelar remoção"):
                st.session_state.pop("email_remocao_pendente", None)
                st.rerun()

    for indice, participante in enumerate(participantes):
        email = participante["email"]
        with st.expander(f"🎁 {participante['nome']} · {email}"):
            with st.form(f"formulario_editar_{indice}"):
                st.text_input("E-mail (não editável)", value=email, disabled=True)
                nome = st.text_input("Nome", value=participante["nome"])
                st.caption("O participante informa e atualiza o próprio endereço no cadastro.")
                salvar = st.form_submit_button("Salvar nome")
            if salvar:
                if not nome.strip():
                    st.warning("O nome é obrigatório.")
                else:
                    try:
                        requisicao_supabase(
                            configuracao,
                            "/rest/v1/participantes",
                            metodo="PATCH",
                            admin=True,
                            params={"email": f"eq.{email}"},
                            dados={"nome": nome.strip()},
                            preferencias="return=minimal",
                        )
                        st.success("Dados atualizados.")
                        st.rerun()
                    except requests.RequestException:
                        st.error("Não foi possível atualizar o participante.")

            if st.button("Gerar link para definir/redefinir senha", key=f"senha_{indice}"):
                try:
                    link = gerar_link_senha(configuracao, email)
                    st.success("Link gerado. Compartilhe-o somente com o dono deste e-mail.")
                    st.code(link, language=None)
                    st.warning("O link é individual, secreto e pode ser usado uma única vez.")
                except (requests.RequestException, ValueError):
                    st.error("Não foi possível gerar o link de senha.")

            if st.button("Remover participante", key=f"remover_{indice}"):
                st.session_state["email_remocao_pendente"] = email
                st.rerun()


def requisicao_do_usuario(configuracao, usuario, caminho, metodo="GET", dados=None,
                          params=None, preferencias="return=minimal"):
    sessao = st.session_state.sessao_supabase
    return requisicao_supabase(
        configuracao,
        caminho,
        metodo=metodo,
        token=sessao["access_token"],
        dados=dados,
        params=params,
        preferencias=preferencias,
    )


def carregar_dados(configuracao, usuario):
    perfil = requisicao_do_usuario(
        configuracao,
        usuario,
        "/rest/v1/participantes",
        params={
            "select": "email,nome,endereco",
            "email": f"eq.{usuario['email'].lower()}",
        },
    )
    participantes = requisicao_do_usuario(
        configuracao,
        usuario,
        "/rest/v1/participantes",
        params={"select": "nome,endereco", "order": "nome.asc"},
    )
    sugestoes = requisicao_do_usuario(
        configuracao,
        usuario,
        "/rest/v1/sugestoes",
        params={"select": "data_hora", "order": "data_hora.asc"},
    )
    ranking = requisicao_do_usuario(
        configuracao,
        usuario,
        "/rest/v1/rpc/ranking_sugestoes",
        metodo="POST",
        dados={},
        preferencias="return=representation",
    )
    return (perfil[0] if perfil else None), participantes, sugestoes, ranking


def salvar_perfil(configuracao, usuario, nome, endereco, perfil_atual):
    email = usuario["email"].strip().lower()
    dados = {
        "email": email,
        "auth_user_id": usuario["id"],
        "nome": nome.strip(),
        "endereco": endereco.strip(),
    }
    if perfil_atual:
        return requisicao_do_usuario(
            configuracao,
            usuario,
            "/rest/v1/participantes",
            metodo="PATCH",
            params={"email": f"eq.{email}", "select": "email"},
            dados={"auth_user_id": usuario["id"], "nome": dados["nome"], "endereco": dados["endereco"]},
            preferencias="return=representation",
        )
    return requisicao_do_usuario(
        configuracao,
        usuario,
        "/rest/v1/participantes",
        metodo="POST",
        dados=dados,
        params={"select": "email"},
        preferencias="return=representation",
    )


def main():
    configuracao = carregar_configuracao()
    if configuracao is None:
        st.error(
            "Configure SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, "
            "INVITE_ADMIN_PASSWORD e APP_URL nos Secrets do Streamlit."
        )
        st.stop()

    cookies = CookieController(key="amigo_secreto_cookies")

    try:
        usuario = validar_sessao(configuracao, cookies)
    except requests.RequestException:
        st.error("Não foi possível validar sua sessão. Tente novamente.")
        limpar_sessao(configuracao, cookies)
        usuario = None

    if not usuario:
        tela_entrada(configuracao, cookies)
        st.stop()

    if st.session_state.get("exigir_nova_senha"):
        tela_definir_senha(configuracao)
        st.stop()

    if st.session_state.pop("senha_atualizada", False):
        st.success("Senha definida. Você já pode acessar sua conta com e-mail e senha.")

    if st.button("Sair"):
        try:
            requisicao_do_usuario(
                configuracao, usuario, "/auth/v1/logout", metodo="POST", dados={}
            )
        except requests.RequestException:
            pass
        limpar_sessao(configuracao, cookies)
        st.rerun()

    render_hero()
    st.caption(f"Conectado como {usuario['email']}")

    try:
        perfil, participantes, sugestoes, ranking = carregar_dados(configuracao, usuario)
    except requests.RequestException:
        st.error("Não foi possível carregar os dados. Confira as políticas do banco no Supabase.")
        st.stop()

    aba_cadastro, aba_sugestoes, aba_ranking = st.tabs(
        ["1️⃣ Cadastro", "2️⃣ Sugerir Datas", "3️⃣ Melhores Dias"]
    )

    with aba_cadastro:
        st.subheader("📍 Seu cadastro")
        st.write("Este é o cadastro associado ao seu e-mail.")
        with st.form("formulario_perfil"):
            nome = st.text_input("Seu Nome", value=perfil["nome"] if perfil else "")
            endereco = st.text_area(
                "Endereço Completo para Entrega",
                value=perfil["endereco"] if perfil else "",
                help="Preencha seu endereço para que o grupo saiba onde entregar seu presente.",
            )
            salvar = st.form_submit_button("Salvar Cadastro")

        if salvar:
            if not nome.strip() or not endereco.strip():
                st.warning("Preencha todos os campos.")
            else:
                try:
                    resultado = salvar_perfil(configuracao, usuario, nome, endereco, perfil)
                    if resultado:
                        st.success("Cadastro salvo para o e-mail autenticado.")
                        st.rerun()
                    st.error("Este cadastro já está vinculado a outra conta autenticada.")
                except requests.HTTPError as erro:
                    if erro.response is not None and erro.response.status_code == 409:
                        st.error("Este e-mail já está associado a outro cadastro.")
                    else:
                        st.error("Não foi possível salvar o cadastro.")
                except requests.RequestException:
                    st.error("Não foi possível acessar o banco de dados.")

        st.write("---")
        st.write(f"**Participantes e endereços ({len(participantes)}):**")
        for participante in participantes:
            st.write(f"👤 **{participante['nome']}**")
            st.text(participante["endereco"])

    with aba_sugestoes:
        st.subheader("📅 Sugerir Datas para a Confra")
        st.write("Você pode sugerir até 10 opções de dias e horários.")
        if not perfil:
            st.info("Complete seu cadastro antes de enviar sugestões.")
        else:
            col_data, col_horario = st.columns(2)
            with col_data:
                data = st.date_input("Data", min_value=datetime.date.today())
            with col_horario:
                horario = st.time_input("Horário")

            if st.button("Enviar Sugestão"):
                data_hora = f"{data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}"
                if len(sugestoes) >= 10:
                    st.error("Você já atingiu o limite de 10 sugestões.")
                elif any(s["data_hora"] == data_hora for s in sugestoes):
                    st.warning("Você já sugeriu essa data e horário.")
                else:
                    try:
                        requisicao_do_usuario(
                            configuracao,
                            usuario,
                            "/rest/v1/sugestoes",
                            metodo="POST",
                            dados={"email": usuario["email"].lower(), "data_hora": data_hora},
                        )
                        st.success("Sugestão adicionada.")
                        st.rerun()
                    except requests.HTTPError as erro:
                        detalhe = erro.response.text.lower() if erro.response is not None else ""
                        if "limite de 10" in detalhe:
                            st.error("Você já atingiu o limite de 10 sugestões.")
                        elif erro.response is not None and erro.response.status_code == 409:
                            st.warning("Você já sugeriu essa data e horário.")
                        else:
                            st.error("Não foi possível salvar a sugestão.")
                    except requests.RequestException:
                        st.error("Não foi possível acessar o banco de dados.")

            if sugestoes:
                st.write(f"**Suas sugestões ({len(sugestoes)}/10):**")
                for sugestao in sugestoes:
                    st.write(f"- 🕒 {sugestao['data_hora']}")

    with aba_ranking:
        st.subheader("🏆 Melhores Dias para a Confra")
        if not ranking:
            st.info("Ainda não temos datas sugeridas.")
        else:
            st.write("Estes são os dias e horários com mais votos:")
            for posicao, item in enumerate(ranking):
                data_hora = item["data_hora"]
                votos = item["votos"]
                texto_votos = "voto" if votos == 1 else "votos"
                if posicao == 0:
                    st.success(f"🥇 **{data_hora}** — {votos} {texto_votos}")
                elif posicao == 1:
                    st.warning(f"🥈 **{data_hora}** — {votos} {texto_votos}")
                elif posicao == 2:
                    st.info(f"🥉 **{data_hora}** — {votos} {texto_votos}")
                else:
                    st.write(f"**{posicao + 1}º lugar:** {data_hora} — {votos} {texto_votos}")


if __name__ == "__main__":
    pagina_configuracao = st.Page(
        tela_configuracao,
        title="Gerenciamento",
        icon="⚙️",
        url_path="config",
    )
    pagina = st.navigation(
        [
            st.Page(main, title="Amigo Secreto", icon="🎁", default=True),
            pagina_configuracao,
        ],
        position="hidden",
    )
    pagina.run()