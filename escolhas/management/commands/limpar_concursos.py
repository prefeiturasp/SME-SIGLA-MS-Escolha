"""
Django management command to clear all concursos.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from concursos.models import Concurso


class Command(BaseCommand):
    help = 'Remove todos os registros da tabela de concursos'

    def handle(self, *args, **options):

        # Contar registros existentes
        total_registros = Concurso.objects.count()
        # Executar a exclusão
        self.stdout.write(
            self.style.SUCCESS(f'Removendo {total_registros} registros...')
        )
        
        try:
            # Método 1: Usando delete() em queryset (mais seguro)
            Concurso.objects.all().delete()
            
            # Método 2: Usando SQL direto (mais rápido, mas menos seguro)
            # with connection.cursor() as cursor:
            #     cursor.execute("DELETE FROM concursos")
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {total_registros} registros removidos com sucesso!')
            )
            
            # Verificar se realmente foi limpo
            registros_restantes = Concurso.objects.count()
            if registros_restantes == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ Tabela completamente limpa!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Ainda restam {registros_restantes} registros.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao remover registros: {e}')
            ) 