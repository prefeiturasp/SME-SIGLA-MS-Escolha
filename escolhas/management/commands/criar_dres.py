"""Django management command to create sample DREs."""
from __future__ import annotations
from typing import Any
from django.core.management.base import BaseCommand
from escolhas.models import Dre

class Command(BaseCommand):
    """Define Command."""
    help = 'Cria DREs de exemplo para desenvolvimento'

    def add_arguments(self, parser: Any) -> None:
        """Registra argumentos da linha de comando.
        
        Args:
            self: Instância do objeto.
            parser: Parâmetro parser da operação.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        parser.add_argument('--count', type=int, default=5, help='Número de DREs a serem criadas (padrão: 5)')

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a lógica principal do comando.
        
        Args:
            self: Instância do objeto.
            *args: Argumentos posicionais variáveis.
            **options: Parâmetro options da operação.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'Criando {count} DREs...'))
        nomes = [('108100', 'DIRETORIA REGIONAL DE EDUCACAO BUTANTA', 'DRE - BT'), ('108200', 'DIRETORIA REGIONAL DE EDUCACAO IPIRANGA', 'DRE - IP'), ('108300', 'DIRETORIA REGIONAL DE EDUCACAO PENHA', 'DRE - PE'), ('108400', 'DIRETORIA REGIONAL DE EDUCACAO PIRITUBA', 'DRE - PI'), ('108500', 'DIRETORIA REGIONAL DE EDUCACAO SANTANA', 'DRE - SA')]
        criadas = []
        for i in range(count):
            codigo, nome, sigla = nomes[i % len(nomes)]
            dre, created = Dre.objects.get_or_create(codigo=codigo, defaults={'nome': nome, 'sigla': sigla})
            if created:
                criadas.append(dre)
                self.stdout.write(f'  ✓ Criada DRE: {dre.sigla} - {dre.nome}')
            else:
                self.stdout.write(f'  - DRE já existe: {dre.sigla} - {dre.nome}')
        self.stdout.write(self.style.SUCCESS(f'✅ {len(criadas)} DREs criadas!'))
