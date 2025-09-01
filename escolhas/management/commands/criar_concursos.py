"""
Django management command to create sample concursos.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from concursos.models import Concurso, Cargo
import uuid
import random


class Command(BaseCommand):
    help = 'Cria concursos de exemplo para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Número de concursos a serem criados (padrão: 5)'
        )
        parser.add_argument(
            '--criar-cargos',
            action='store_true',
            help='Criar cargos de exemplo e associá-los aos concursos'
        )

    def handle(self, *args, **options):
        count = options['count']
        criar_cargos = options['criar_cargos']
        
        self.stdout.write(
            self.style.SUCCESS(f'Criando {count} concursos...')
        )
        
        # Criar cargos de exemplo se solicitado
        cargos_disponiveis = []
        if criar_cargos:
            cargos_nomes = [
                'Analista de Sistemas',
                'Desenvolvedor Backend',
                'Desenvolvedor Frontend',
                'Analista de Dados',
                'Engenheiro de Software',
                'Arquiteto de Software',
                'DevOps Engineer',
                'QA Engineer',
                'Product Manager',
                'UX/UI Designer'
            ]
            
            self.stdout.write('Criando cargos de exemplo...')
            for nome in cargos_nomes:
                cargo, created = Cargo.objects.get_or_create(nome=nome)
                cargos_disponiveis.append(cargo)
                if created:
                    self.stdout.write(f'  ✓ Criado cargo: {nome}')
                else:
                    self.stdout.write(f'  - Cargo já existe: {nome}')
        
        concursos_criados = []
        
        for i in range(count):
            # Criar concurso com nome único
            nome_concurso = f'Concurso de Exemplo {i+1}'
            
            concurso = Concurso.objects.create(
                nome=nome_concurso
            )
            
            # Associar cargos aleatórios se disponíveis
            if cargos_disponiveis:
                num_cargos = random.randint(1, min(3, len(cargos_disponiveis)))
                cargos_escolhidos = random.sample(cargos_disponiveis, num_cargos)
                concurso.cargos.set(cargos_escolhidos)
                
                cargos_info = ', '.join([cargo.nome for cargo in cargos_escolhidos])
                self.stdout.write(
                    f'  ✓ Criado concurso: {concurso.nome} '
                    f'(Cargos: {cargos_info})'
                )
            else:
                self.stdout.write(
                    f'  ✓ Criado concurso: {concurso.nome} (sem cargos)'
                )
            
            concursos_criados.append(concurso)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {len(concursos_criados)} concursos criados com sucesso!'
            )
        )
        
        if criar_cargos:
            self.stdout.write(
                self.style.SUCCESS(
                    f'📋 {len(cargos_disponiveis)} cargos disponíveis para associação.'
                )
            ) 