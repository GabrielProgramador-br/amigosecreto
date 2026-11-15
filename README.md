# Amigo Secreto Online

O app usa Supabase Auth para entrar com e-mail e senha. O gerente administra participantes em `/config`, onde cadastra cada pessoa com nome e e-mail, edita nomes, remove pessoas e gera links para definir ou redefinir senhas. Cada participante informa o proprio endereco no cadastro da conta. Os links sao exibidos no app para compartilhamento manual; nenhum e-mail e enviado automaticamente. A sessao fica persistida no navegador por ate 30 dias ou ate a pessoa sair. Todos os participantes autenticados podem ver os nomes e enderecos uns dos outros; visitantes sem conta nao podem acessar esses dados.

## Visual natalino

A interface tem luzes decorativas e ilustracao natalina, cards de participantes, indicadores de cadastro e sugestoes, e ranking com destaque para a data mais votada. O layout se adapta a telas menores e respeita a preferencia por movimento reduzido. Os indicadores mostram os dados atuais do grupo; nao alteram as regras de participacao.

## Configurar o banco

1. Crie um projeto no Supabase.
2. No SQL Editor do projeto, execute o conteudo de `supabase_schema.sql`. O script tambem adiciona o vinculo de autenticacao caso as tabelas da versao anterior ja existam.
3. Desative o cadastro publico de usuarios. As contas devem ser criadas pelo gerente na area `/config`.
4. Copie a URL e a chave publica (anon/publishable) e a chave secreta (service_role/secret) nas configuracoes do app. A chave secreta e usada somente no servidor para administrar contas e gerar links de senha.

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

4. Publique o app. O gerente acessa `https://SEU-APP.streamlit.app/config`, informa `INVITE_ADMIN_PASSWORD` e cadastra cada participante com nome e e-mail.
5. Copie o link de senha gerado e compartilhe-o em mensagem privada com o participante. Ao abrir o link, a pessoa define a senha e depois entra pela tela inicial usando e-mail e senha. Para redefinir uma senha, gere outro link no cadastro da pessoa em `/config`.

Nao e necessario configurar SMTP. Os links sao credenciais temporarias de uso unico; quem tiver acesso ao link podera definir ou redefinir a senha daquela conta. Compartilhe cada link somente com o dono do e-mail correspondente.

O GitHub Pages nao executa apps Python/Streamlit; use o Streamlit Community Cloud ou outro servico que execute Python.

## Executar localmente

Instale as dependencias de `requirements.txt` e crie `.streamlit/secrets.toml` com os mesmos valores acima. Esse arquivo esta no `.gitignore` para evitar o envio de credenciais ao GitHub.

```powershell
python -m pip install -r requirements.txt
streamlit run main.py
```

## Limites de identidade e privacidade

O app pede um clique adicional antes de consumir o token. O cookie de sessao guarda o refresh token no navegador por ate 30 dias; use **Sair** em dispositivos compartilhados. Mantenha privada a senha do gerente e nunca compartilhe a chave `service_role`; ela permite operacoes administrativas. Trate cada link gerado como uma credencial: envie-o apenas ao participante correspondente e gere outro se for compartilhado por engano. As politicas RLS limitam as gravacoes a identidade autenticada e restringem a leitura ao grupo autenticado. Cada participante pode ver os enderecos cadastrados, portanto convide apenas pessoas autorizadas a acessar esses dados.