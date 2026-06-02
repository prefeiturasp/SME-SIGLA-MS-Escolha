"""
Django management command to create sample Escolas.
"""

import random

from django.core.management.base import BaseCommand

from escolhas.models import Dre, Escola


class Command(BaseCommand):
    help = "Cria escolas de exemplo para desenvolvimento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Número de escolas a serem criadas (padrão: 5)",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(self.style.SUCCESS(f"Criando {count} escolas..."))

        # Garantir que exista ao menos uma DRE
        dre, _ = Dre.objects.get_or_create(
            codigo="108100",
            defaults={
                "nome": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
                "sigla": "DRE - BT",
            },
        )

        bairros = ["JARDIM TABOÃO", "VILA SONIA", "BUTANTA", "IPIRANGA"]
        tipos_ue = [
            "ESCOLA MUNICIPAL DE EDUCACAO INFANTIL",
            "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
        ]

        criadas = []
        for i in range(count):
            item = Escola.objects.create(
                dre=dre,
                codigo_eol=f"{random.randint(100000, 999999)}",
                nome_oficial=f"ESCOLA MUNICIPAL {i+1}",
                nome_nao_oficial=f"EM {i+1}",
                tipo_unidade_admin="DIRETORIA REGIONAL DE EDUCACAO",
                tipo_ue=random.choice(tipos_ue),
                logradouro="Rua Exemplo",
                numero=str(10 + i),
                bairro=random.choice(bairros),
                cep=5742100 + i,
                distrito="DISTRITO EXEMPLO",
                sub_prefeitura="BUTANTA",
                nome_dre=dre.nome,
                email=f"escola{i+1}@sme.prefeitura.sp.gov.br",
                telefone1="(11) 0000-0000",
                telefone2="(11) 0000-0001",
                ano_construcao=1980 + i,
                propriedade="PROPRIO",
                capacidade_vagas_matutino=random.randint(100, 3000),
                capacidade_vagas_vespertino=random.randint(100, 3000),
                capacidade_vagas_noturno=0,
                capacidade_vagas_intermediario=0,
                capacidade_vagas_integral=0,
                capacidade_vagas_total=random.randint(200, 6000),
                organizacao_parceira=bool(random.getrandbits(1)),
                quantidade_de_funcionarios=random.randint(5, 100),
                status="ATIVA",
            )
            criadas.append(item)
            self.stdout.write(
                f"  ✓ Criada escola: {item.nome_oficial} ({item.codigo_eol})"
            )

        self.stdout.write(
            self.style.SUCCESS(f"✅ {len(criadas)} escolas criadas!")
        )
