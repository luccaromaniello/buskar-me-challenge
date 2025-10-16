## Instalação

### Pré-requisitos
- Python 3.10 ou superior
- Git
- Pip

### Clone o repositório

```bash
git clone https://github.com/luccaromaniello/buskar-me-challenge.git
cd buskar-me-challenge
```
### Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```
### Instale as dependências

```bash
pip install -r requirements.txt
```

### Crie um banco de dados e sua URL de conexão
Eu utilizei o (Render)[https://render.com/]. Crie um banco de dados PostgreSQL e copie sua *External URL*.

### Adicionar o Bot do Discord no servidor

- Vá para o (Discord Developer Portal)[https://discord.com/developers/applications]
- Clique em *New Application* e selecione um nome para o bot.
- Vá até a aba "OAuth2" > "URL Generator"
- Preencha os seguintes campos:

Scopes:
- bot

Bot Permissions:
- Send Messages
- Read Message History
- View Channels

- Vá em “Bot” no menu lateral.
- Role até “Privileged Gateway Intents”.
- Ative o checkbox “Message Content Intent”.

Em integration type, selecione Guild Install.

Um URL será gerado no final da página — copie esse link. Exemplo:
```bash
https://discord.com/oauth2/authorize?client_id=123456789012345678&scope=bot&permissions=3072
```

- Abra o link copiado no navegador
- Escolha o servidor no qual você tem permissão para adicionar bots
- Autorize o bot

O bot agora aparecerá offline no servidor (isso é normal até você rodar o script). Siga os passos em "Execução" para rodar o bot.

Assim que você rodar o discord_bot.py, ele ficará online e pronto para responder comandos.

### Variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto seguindo o modelo `.env.example`.

#### URL do banco de dados
```bash
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco # sua External URL do Render
```
#### Token e Authorized IDs do Discord
##### Ativar o modo de desenvolvedor no Discord
- Esse é um recurso que permite copiar IDs diretamente.
- Vá em Configurações do Usuário (ícone de engrenagem no canto inferior esquerdo).
- Navegue até Avançado (ou "Advanced", se estiver em inglês).
- Ative a opção "Modo de desenvolvedor".

##### Copiar IDs do Discord
- Clique com o botão direito sobre seu nome de usuário (ou o de outro usuário).
- Clique em "Copiar ID".
- Você verá algo como: `123456789012345678`

Esse é o ID que você deve colocar no seu `.env`, na variável `AUTHORIZED_IDS`.
```bash
AUTHORIZED_IDS=123456789012345678 # Você pode colocar vários IDs separados por vírgula, sem espaços.
```
#### Token do Discord
```bash
DISCORD_BOT_TOKEN=seutoken # Disponível na aba Bot dentro da sua aplicação no Discord Developer Portal
```
#### URL da API
Em desenvolvimento, você pode usar o servidor local. Também pode utilizar a API remota na URL `xxxxx`.
```bash
API_URL=http://localhost:8000
```

---

## Execução

### Ambiente virtual
Crie um ambiente virtual usando o Python 3.8 ou superior:
```bash
python -m venv venv
```
Ative o ambiente virtual:
```bash
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```
Depois da ativação, seu prompt do terminal deve mudar para mostrar seu ambiente virtual:
```bash
(venv) seu-usuario$
```

### Servidor
Na raiz do projeto, execute o seguinte comando para iniciar o servidor:
```bash
uvicorn server:app --reload
```
O servidor estará disponível em `http://localhost:8000` ou `http://localhost:8000/docs` (Documentação automática - FastAPI). Você pode fazer requisições usando CURL ou algum software como Postman/Insomnia.

### Bot do Discord
Em outra instância do terminal, na raiz do projeto, execute o seguinte comando para iniciar o bot:
```bash
python discord_bot.py
```

## Finalizar execução
Para finalizar o bot, pressione `Ctrl+C` no terminal onde ele está sendo executado.
Para finalizar o servidor, pressione `Ctrl+C` no terminal onde ele está sendo executado.
Você pode sair do ambiente virtual digitando `deactivate` no terminal.
