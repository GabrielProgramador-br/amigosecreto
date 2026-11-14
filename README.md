# Amigo Secreto Online

O app usa Supabase Auth para gerar links individuais de convite e acesso, sem enviar e-mails. O organizador compartilha cada link diretamente com o participante correspondente. A sessao fica persistida no navegador por ate 30 dias ou ate a pessoa sair. Todos os participantes autenticados podem ver os nomes e enderecos uns dos outros; visitantes sem convite nao podem acessar esses dados.

## Configurar o banco

1. Crie um projeto no Supabase.
2. No SQL Editor do projeto, execute o conteudo de `supabase_schema.sql`. O script tambem adiciona o vinculo de autenticacao caso as tabelas da versao anterior ja existam.
3. Desative o cadastro publico de usuarios. As contas devem ser criadas apenas pelo link de convite gerado pelo organizador.
4. Copie a URL e a chave publica (anon/publishable) e a chave secreta (service_role/secret) nas configuracoes do app. A chave secreta e usada somente no servidor para gerar links administrativos.

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

4. Publique o app. O organizador abre a area de convites, seleciona **Convite inicial**, informa o e-mail e gera um link individual para compartilhar em mensagem privada.
5. Se o participante ja aceitou o convite e precisa entrar novamente, gere **Novo link de acesso** para o e-mail dele.

Nao e necessario configurar SMTP. O link de cada pessoa e exibido ao organizador no app e deve ser compartilhado somente com o dono daquele e-mail. Links sao credenciais temporarias de uso unico; quem tiver acesso ao link podera entrar como aquele participante.

O GitHub Pages nao executa apps Python/Streamlit; use o Streamlit Community Cloud ou outro servico que execute Python.

## Executar localmente

Instale as dependencias de `requirements.txt` e crie `.streamlit/secrets.toml` com os mesmos valores acima. Esse arquivo esta no `.gitignore` para evitar o envio de credenciais ao GitHub.

```powershell
python -m pip install -r requirements.txt
streamlit run main.py
```

## Limites de identidade e privacidade

O app pede um clique adicional antes de consumir o token. O cookie de sessao guarda o refresh token no navegador por ate 30 dias; use **Sair** em dispositivos compartilhados. Mantenha privada a senha do organizador e nunca compartilhe a chave `service_role`; ela permite operacoes administrativas. Trate cada link gerado como uma credencial: envie-o apenas ao participante correspondente e gere outro se for compartilhado por engano. As politicas RLS limitam as gravacoes a identidade autenticada e restringem a leitura ao grupo autenticado. Cada participante pode ver os enderecos cadastrados, portanto convide apenas pessoas autorizadas a acessar esses dados.