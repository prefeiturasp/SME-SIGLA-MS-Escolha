# Requirements Structure

Esta pasta contém os arquivos de dependências organizados por ambiente.

## 📁 Estrutura

```
requirements/
├── base.txt          # Dependências principais (Django, DRF, etc.)
├── local.txt         # Dependências para desenvolvimento local
├── production.txt    # Dependências para produção
└── README.md        # Este arquivo
```

## 🚀 Como usar

### Desenvolvimento Local
```bash
pip install -r requirements/local.txt
```

### Produção
```bash
pip install -r requirements/production.txt
```

### Instalação padrão (desenvolvimento)
```bash
pip install -r requirements.txt
```

## 📋 Conteúdo dos arquivos

### base.txt
- Django e DRF
- PostgreSQL driver
- Requests
- Decouple para variáveis de ambiente

### local.txt
- Inclui base.txt
- Ferramentas de teste (pytest)
- Qualidade de código (black, flake8)
- Documentação (Sphinx)
- Extensões de desenvolvimento

### production.txt
- Inclui base.txt
- Servidor WSGI (gunicorn)
- Arquivos estáticos (whitenoise)
- Segurança
- Monitoramento (Sentry)
- Performance e health checks

## 🔧 Desenvolvimento

Para adicionar novas dependências:

1. **Dependências principais**: Adicione em `base.txt`
2. **Desenvolvimento**: Adicione em `local.txt`
3. **Produção**: Adicione em `production.txt`

## 📦 Instalação em diferentes ambientes

### Desenvolvimento
```bash
# Instalar todas as dependências de desenvolvimento
pip install -r requirements/local.txt

# Ou usar o arquivo padrão
pip install -r requirements.txt
```

### Produção
```bash
# Instalar apenas dependências de produção
pip install -r requirements/production.txt
```

### Docker
```dockerfile
# No Dockerfile, use:
COPY requirements/production.txt /app/requirements.txt
RUN pip install -r requirements.txt
``` 