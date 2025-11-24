# Makefile para o projeto SME-SIGLA-MS-Escolha
# Comandos úteis para desenvolvimento Django

.PHONY: help makemigrations migrate runserver coverage test clean install

# Comando padrão - mostra ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make makemigrations  - Cria migrações do Django"
	@echo "  make migrate         - Aplica migrações do Django"
	@echo "  make runserver       - Inicia o servidor de desenvolvimento"
	@echo "  make coverage        - Executa testes com relatório de cobertura"
	@echo "  make test            - Executa todos os testes"
	@echo "  make clean           - Remove arquivos temporários"
	@echo "  make install         - Instala dependências"

# Cria migrações do Django
makemigrations:
	@echo "Criando migrações..."
	python manage.py makemigrations

# Aplica migrações do Django
migrate:
	@echo "Aplicando migrações..."
	python manage.py migrate

# Inicia o servidor de desenvolvimento
runserver:
	@echo "Iniciando servidor de desenvolvimento..."
	python manage.py runserver

# Executa testes com relatório de cobertura
coverage:
	@echo "Executando testes com cobertura..."
	pytest --ds=config.settings_test --cov=escolhas --cov-report=term-missing --cov-report=html

# Executa todos os testes
test:
	@echo "Executando todos os testes..."
	pytest --ds=config.settings_test

# Remove arquivos temporários
clean:
	@echo "Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Instala dependências
install:
	@echo "Instalando dependências..."
	pip install -r requirements/local.txt
