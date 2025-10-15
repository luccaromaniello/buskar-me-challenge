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

### Crie um arquivo .env na raiz do projeto seguindo o modelo `.env.example`

```bash
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco # sua External URL do Render
```
---

## Execução

### Servidor
Na raiz do projeto, execute o seguinte comando para iniciar o servidor:
```bash
uvicorn server:app --reload
```
O servidor estará disponível em `http://localhost:8000` ou `http://localhost:8000/docs` (Documentação automática - FastAPI). Você pode fazer requisições usando CURL ou algum software como Postman/Insomnia.

### Bot do Discord
