# Docker Setup para Processos de Convocação

Este projeto inclui uma configuração Docker Compose com PostgreSQL para desenvolvimento.

## 🐳 Configuração do Docker

### 1. Iniciar os serviços

```bash
# Iniciar PostgreSQL e pgAdmin
docker-compose up -d

# Verificar se os containers estão rodando
docker-compose ps
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=convocacao_db
DB_USER=convocacao_user
DB_PASSWORD=convocacao_pass
DB_HOST=localhost
DB_PORT=5432
```

### 3. Instalar dependências do Django

```bash
# Para desenvolvimento local
pip install -r requirements/local.txt

# Para produção
pip install -r requirements/production.txt

# Ou usar o arquivo padrão (desenvolvimento)
pip install -r requirements.txt
```

### 4. Executar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar superusuário (opcional)

```bash
python manage.py createsuperuser
```

## 📊 Acessos

### PostgreSQL
- **Host**: localhost
- **Porta**: 5432
- **Database**: concursos
- **Usuário**: postgres
- **Senha**: postgres

### pgAdmin (Interface Web)
- **URL**: http://localhost:8080
- **Email**: admin@convocacao.com
- **Senha**: admin123

Para conectar o pgAdmin ao PostgreSQL:
1. Acesse http://localhost:8080
2. Faça login com as credenciais acima
3. Adicione um novo servidor:
   - **Name**: Convocacao DB
   - **Host**: db (nome do container)
   - **Port**: 5432
   - **Database**: concursos
   - **Username**: postgres
   - **Password**: postgres

## 🛠️ Comandos úteis

```bash
# Parar os serviços
docker-compose down

# Parar e remover volumes (cuidado: apaga os dados)
docker-compose down -v

# Ver logs
docker-compose logs db
docker-compose logs pgadmin

# Acessar o container do PostgreSQL
docker-compose exec db psql -U postgres -d concursos
```

## 🔧 Configurações do PostgreSQL

O container PostgreSQL está configurado com:
- **Versão**: PostgreSQL 17
- **Database**: concursos
- **Usuário**: postgres
- **Senha**: postgres
- **Porta**: 5432
- **Persistência**: Volume `postgres_data`

## 🚀 Desenvolvimento

Com o banco rodando, você pode:

1. Executar o servidor Django:
```bash
python manage.py runserver
```

2. Acessar o admin Django:
   - URL: http://localhost:8000/admin
   - Use o superusuário criado

3. Testar a API:
   - URL: http://localhost:8000/api/ 