import datetime
import hmac
from collections import Counter
from urllib.parse import urlencode

import requests
import streamlit as st
from streamlit_cookies_controller import CookieController

COOKIE_SESSAO = "amigo_secreto_refresh_token"
COOKIE_SESSAO_DURACAO = 30 * 24 * 60 * 60

st.set_page_config(
    page_title="Amigo Secreto Online",
    page_icon="🎁",
    layout="centered",
)

st.markdown("""
    <style>
    .stApp { background-color: #fdfbf7; }
    h1, h2, h3 { color: #d32f2f; font-family: 'Arial', sans-serif; }
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #b71c1c; color: white; }
    </style>
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
    if not token_hash or tipo not in {"invite", "email", "magiclink"}:
        return False

    st.subheader("Confirmar acesso ao Amigo Secreto")
    st.write("Confirme para ativar o link individual compartilhado pelo organizador.")
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

    st.title("🎁 Amigo Secreto Online")
    st.subheader("Acessar com link individual")
    st.write("Peça ao organizador um link para o e-mail que foi convidado.")

    with st.expander("Área do organizador: convidar participante"):
        with st.form("formulario_convite"):
            senha = st.text_input("Senha do organizador", type="password")
            email_convidado = st.text_input("E-mail do participante").strip().lower()
            tipo_link = st.selectbox(
                "Tipo de link",
                options=["Convite inicial", "Novo link de acesso"],
            )
            gerar_convite = st.form_submit_button("Gerar link")

        if gerar_convite:
            if not hmac.compare_digest(senha, configuracao["senha_organizador"]):
                st.error("Senha do organizador incorreta.")
            elif not email_convidado:
                st.warning("Informe o e-mail do participante.")
            else:
                try:
                    tipo_autenticacao = "invite" if tipo_link == "Convite inicial" else "magiclink"
                    resultado = requisicao_supabase(
                        configuracao,
                        "/auth/v1/admin/generate_link",
                        metodo="POST",
                        admin=True,
                        dados={"type": tipo_autenticacao, "email": email_convidado},
                    )
                    propriedades = resultado.get("properties", resultado)
                    token_hash = propriedades.get("hashed_token")
                    tipo_verificacao = propriedades.get("verification_type", tipo_autenticacao)
                    if not token_hash:
                        st.error("O Supabase não retornou o token do link. Confira as configurações do projeto.")
                    else:
                        query = urlencode({"token_hash": token_hash, "type": tipo_verificacao})
                        link_individual = f"{configuracao['app_url']}/?{query}"
                        st.success("Link gerado. Compartilhe-o somente com a pessoa deste e-mail.")
                        st.code(link_individual, language=None)
                        st.warning("O link é individual, secreto e pode ser usado uma única vez.")
                except requests.HTTPError as erro:
                    if erro.response is not None and erro.response.status_code == 422:
                        st.error("Não foi possível gerar o link. Se a conta já existe, escolha Novo link de acesso.")
                    else:
                        st.error("Falha ao gerar link. Confira a chave administrativa do Supabase.")
                except requests.RequestException:
                    st.error("Não foi possível conectar ao serviço de autenticação.")


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

    if st.button("Sair"):
        try:
            requisicao_do_usuario(
                configuracao, usuario, "/auth/v1/logout", metodo="POST", dados={}
            )
        except requests.RequestException:
            pass
        limpar_sessao(configuracao, cookies)
        st.rerun()

    st.title("🎁 Amigo Secreto Online")
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
        st.write("Seu e-mail foi confirmado pelo link de convite.")
        with st.form("formulario_perfil"):
            nome = st.text_input("Seu Nome", value=perfil["nome"] if perfil else "")
            endereco = st.text_area(
                "Endereço Completo para Entrega",
                value=perfil["endereco"] if perfil else "",
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
    main()