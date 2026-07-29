# Comandos Customizados do Django

Esta pasta contém comandos customizados do Django para facilitar o desenvolvimento e manutenção do sistema de processos de convocação.

## 📁 Estrutura

```
management/
├── __init__.py
├── commands/
│   ├── __init__.py
│   ├── create_sample_processos.py
│   ├── cleanup_processos.py
│   ├── clear_processos.py
│   ├── truncate_processos.py
│   └── check_processos.py
└── README.md
```

## 🚀 Comandos Disponíveis

### 1. `create_sample_processos`

Cria processos de exemplo para desenvolvimento com valores aleatórios.

```bash
# Criar 5 processos com valores aleatórios (padrão)
python manage.py create_sample_processos

# Criar 10 processos com valores aleatórios
python manage.py create_sample_processos --count 10

# Criar 20 processos com valores aleatórios
python manage.py create_sample_processos --count 20
```

**Opções:**
- `--count`: Número de processos a criar (padrão: 5)

**Campos aleatorizados:**
- Status: EM_ANDAMENTO, FINALIZADO, CANCELADO
- Tipo de processo: CONVOCACAO, SELECAO, AVALIACAO
- Descrição: Todas as opções de descrição disponíveis

### 2. `cleanup_processos`

Remove processos antigos ou cancelados.

```bash
# Remover processos cancelados com mais de 30 dias
python manage.py cleanup_processos

# Remover processos finalizados com mais de 60 dias
python manage.py cleanup_processos --days 60 --status FINALIZADO

# Ver o que seria removido sem executar
python manage.py cleanup_processos --dry-run
```

**Opções:**
- `--days`: Dias para considerar como "antigo" (padrão: 30)
- `--status`: Status dos processos a remover (FINALIZADO, CANCELADO)
- `--dry-run`: Mostra o que seria removido sem executar

### 3. `export_processos`

Exporta processos para arquivo JSON.

```bash
# Exportar todos os processos
python manage.py export_processos

# Exportar apenas processos em andamento
python manage.py export_processos --status EM_ANDAMENTO

# Exportar apenas 10 processos
python manage.py export_processos --limit 10

# Exportar para arquivo específico
python manage.py export_processos --output meus_processos.json
```

**Opções:**
- `--output`: Nome do arquivo de saída (padrão: processos_export.json)
- `--status`: Filtrar por status específico
- `--limit`: Limitar número de processos exportados

### 4. `clear_processos`

Remove todos os registros da tabela de processos.

```bash
# Ver quantos registros seriam removidos
python manage.py clear_processos --dry-run

# Remover com confirmação interativa
python manage.py clear_processos

# Remover sem confirmação
python manage.py clear_processos --confirm
```

**Opções:**
- `--dry-run`: Mostra quantos registros seriam removidos
- `--confirm`: Confirma a exclusão sem pedir confirmação

### 5. `truncate_processos`

Trunca a tabela usando SQL direto (mais rápido).

```bash
# Ver o que seria executado
python manage.py truncate_processos --dry-run

# Truncar com confirmação interativa
python manage.py truncate_processos

# Truncar sem confirmação
python manage.py truncate_processos --confirm
```

**Opções:**
- `--dry-run`: Mostra o comando SQL que seria executado
- `--confirm`: Confirma a exclusão sem pedir confirmação

### 6. `check_processos`

Verifica a integridade e mostra estatísticas dos processos.

```bash
# Verificação básica
python manage.py check_processos

# Verificação detalhada
python manage.py check_processos --detailed
```

**Funcionalidades:**
- Estatísticas gerais
- Contagem por status e tipo
- Verificação de integridade
- Detalhes dos processos (com --detailed)

## 📊 Exemplos de Uso

### Desenvolvimento

```bash
# 1. Criar dados de teste com valores aleatórios
python manage.py create_sample_processos --count 20

# 2. Verificar integridade
python manage.py check_processos --detailed

# 3. Limpar dados de teste
python manage.py clear_processos --confirm
```

### Produção

```bash
# 1. Verificar integridade
python manage.py check_processos

# 2. Limpar processos antigos (dry-run primeiro)
python manage.py cleanup_processos --dry-run
python manage.py cleanup_processos --days 90 --status CANCELADO

# 3. Limpar tabela completamente
python manage.py truncate_processos --confirm
```

## 🔧 Criando Novos Comandos

Para criar um novo comando customizado:

1. Crie um arquivo em `management/commands/`
2. Herde de `BaseCommand`
3. Implemente o método `handle()`

Exemplo:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Descrição do comando'
    
    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Descrição da opção')
    
    def handle(self, *args, **options):
        # Lógica do comando
        self.stdout.write(self.style.SUCCESS('Comando executado!'))
```

## 📝 Boas Práticas

1. **Sempre use `--dry-run`** antes de comandos destrutivos
2. **Documente as opções** com `help`
3. **Use cores** para melhor visualização (`self.style.SUCCESS`, `self.style.WARNING`)
4. **Trate exceções** adequadamente
5. **Teste os comandos** antes de usar em produção 