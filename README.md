# Amigo Secreto Online

O app usa Supabase Auth para convidar cada participante por e-mail. A identidade confirmada e vinculada ao cadastro e as sugestoes no banco. Todos os participantes autenticados podem ver os nomes e enderecos uns dos outros; visitantes sem convite nao podem acessar esses dados.

## Configurar o banco

1. Crie um projeto no Supabase.
2. No SQL Editor do projeto, execute o conteudo de `supabase_schema.sql`. O script tambem adiciona o vinculo de autenticacao caso as tabelas da versao anterior ja existam.
3. Em Authentication > URL Configuration, configure a Site URL com a URL final do app e adicione essa URL a lista de redirecionamentos permitidos.
4. Desative o cadastro publico de usuarios. O app envia links de login apenas para contas criadas por convite.
5. Em Authentication > Email Templates, altere os links dos templates **Invite user** e **Magic Link** para apontar ao app e deixar a confirmacao para um clique manual:

```html
<!-- Template Invite user -->
<a href="{{ .SiteURL }}/?token_hash={{ .TokenHash }}&type=invite">Aceitar convite</a>

<!-- Template Magic Link -->
<a href="{{ .SiteURL }}/?token_hash={{ .TokenHash }}&type=email">Entrar no Amigo Secreto</a>
```

6. Configure um provedor SMTP para envio confiavel de e-mails.
7. Copie a URL, a chave publica (anon/publishable) e a chave secreta (service_role/secret) nas configuracoes do app. A chave secreta e usada apenas no servidor para enviar convites.

## Publicar pelo Streamlit Community Cloud

1. Envie este projeto para um repositorio GitHub.
2. No Streamlit Community Cloud, crie um app apontando para esse repositorio e selecione `main.py`.
3. Nas configuracoes avancadas do app, adicione estes Secrets em formato TOML:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_ANON_KEY = "SUA_CHAVE_PUBLICA"
SUPABASE_SERVICE_ROLE_KEY = "SUA_CHAVE_SERVICE_ROLE"
INVITE_ADMIN_PASSWORD = "SENHA_FORTE_DO_ORGANIZADOR"
APP_URL = "https://SEU-APP.streamlit.app"
```

4. Publique o app. O organizador entra na area de convites e envia um link individual para cada participante.
5. O participante confirma o convite, completa o cadastro e depois pode solicitar novos links de login pelo e-mail.

O GitHub Pages nao executa apps Python/Streamlit; use o Streamlit Community Cloud ou outro servico que execute Python.

## Executar localmente

Instale as dependencias e crie `.streamlit/secrets.toml` com os mesmos valores acima. Esse arquivo esta no `.gitignore` para evitar o envio de credenciais ao GitHub.

```powershell
python -m pip install -r requirements.txt
streamlit run main.py
```

## Limites de identidade e privacidade

O link de convite e enviado ao e-mail pela Auth do Supabase. O app pede um clique adicional antes de consumir o token para reduzir o risco de scanners de e-mail usarem o link automaticamente. Mantenha privada a senha do organizador e nunca compartilhe a chave `service_role`; ela permite operacoes administrativas. As politicas RLS limitam as gravacoes a identidade autenticada e restringem a leitura ao grupo autenticado. Cada participante do grupo pode ver os enderecos cadastrados, portanto convide apenas pessoas autorizadas a acessar esses dados.