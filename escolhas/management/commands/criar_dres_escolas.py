"""
Django management command to fetch DREs from SME Integracao and upsert records.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from escolhas.models import Dre, Escola
from escolhas.services.sme_integration import (
    buscar_dres_de_smeintegracao,
    buscar_ues_codigos_por_dre,
    buscar_dados_escola_por_eol,
)


class Command(BaseCommand):
    help = 'Busca DREs na SME Integracao (/api/DREs) e cria/atualiza registros locais'


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Buscando DREs da SME Integracao...'))

        try:
            dres = buscar_dres_de_smeintegracao()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Falha ao buscar DREs: {exc}'))
            return

        self.stdout.write(f'Encontradas {len(dres)} DREs no serviço externo')

        created_count = 0
        updated_count = 0
        skipped_count = 0


        with transaction.atomic():
            for item in dres:
                codigo = item['codigo']
                nome = item['nome']
                sigla = item['sigla']

                dre, created = Dre.objects.get_or_create(
                    codigo=codigo,
                    defaults={'nome': nome, 'sigla': sigla}
                )

                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Criada DRE: {dre.sigla} - {dre.nome}')
                    continue

                if dre.nome == nome and dre.sigla == sigla:
                    skipped_count += 1
                    self.stdout.write(f'  - Sem alterações: {dre.sigla} - {dre.nome}')
                    continue

                changed = False
                if dre.nome != nome:
                    dre.nome = nome
                    changed = True
                if dre.sigla != sigla:
                    dre.sigla = sigla
                    changed = True

                if changed:
                    dre.save(update_fields=['nome', 'sigla'])
                    updated_count += 1
                    self.stdout.write(f'  ↻ Atualizada DRE: {dre.sigla} - {dre.nome}')

        self.stdout.write(self.style.SUCCESS(
            f'✅ Concluído: criadas={created_count}, atualizadas={updated_count}, sem_alteracao={skipped_count}'
        ))

        self.stdout.write(self.style.SUCCESS('Iniciando sincronização de escolas por DRE...'))

        escolas_criadas = 0
        escolas_atualizadas = 0
        escolas_sem_alteracao = 0

        dres_qs = Dre.objects.all().order_by('codigo')
        for dre in dres_qs:
            self.stdout.write(self.style.HTTP_INFO(f'Consultando UEs da DRE {dre.sigla} ({dre.codigo})...'))

            try:
                codigos_ue = buscar_ues_codigos_por_dre(dre.codigo)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'  Falha ao buscar UEs da DRE {dre.codigo}: {exc}'))
                continue

            self.stdout.write(f'  Encontradas {len(codigos_ue)} UEs para a DRE {dre.codigo}')

            for codigo_eol in codigos_ue:
                try:
                    dados = buscar_dados_escola_por_eol(codigo_eol)
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f'  Falha ao buscar escola {codigo_eol}: {exc}'))
                    continue

                nome_dre = (dados.get('nomeDRE') or '').strip() or dre.nome
                sigla_tipo_escola = (dados.get('siglaTipoEscola') or '').strip()
                tipo_unidade = (dados.get('tipoUnidade') or '').strip()
                desc_tipo_unidade_adm = (dados.get('descTipoUnidadeAdm') or '').strip()

                tipo_ue_val = sigla_tipo_escola or tipo_unidade or 'DESCONHECIDO'
                tipo_unidade_admin_val = desc_tipo_unidade_adm or 'DESCONHECIDO'

                tipo_logradouro = (dados.get('tipoLogradouro') or '').strip()
                logradouro_nome = (dados.get('logradouro') or '').strip()
                logradouro_val = f"{tipo_logradouro} {logradouro_nome}".strip() if tipo_logradouro else logradouro_nome

                numero_val = str(dados.get('numero') or '').strip()
                bairro_val = (dados.get('bairro') or '').strip()
                cep_val_raw = dados.get('cep')
                try:
                    cep_val = int(cep_val_raw) if cep_val_raw is not None and str(cep_val_raw).strip() != '' else 0
                except (TypeError, ValueError):
                    cep_val = 0

                escola_defaults = {
                    'dre': dre,
                    'nome_oficial': (dados.get('nome') or '').strip() or 'DESCONHECIDO',
                    'nome_nao_oficial': (dados.get('nomeExibicao') or '').strip() or None,
                    'tipo_unidade_admin': tipo_unidade_admin_val,
                    'tipo_ue': tipo_ue_val,
                    'logradouro': logradouro_val or 'DESCONHECIDO',
                    'numero': numero_val or 'S/N',
                    'bairro': bairro_val or 'DESCONHECIDO',
                    'cep': cep_val,
                    'distrito': 'DESCONHECIDO',
                    'sub_prefeitura': 'DESCONHECIDA',
                    'nome_dre': nome_dre,
                    'email': (dados.get('email') or '').strip() or None,
                    'telefone1': (dados.get('telefone') or '').strip() or None,
                    'telefone2': None,
                    'ano_construcao': None,
                    'propriedade': 'DESCONHECIDO',
                    'capacidade_vagas_matutino': 0,
                    'capacidade_vagas_vespertino': 0,
                    'capacidade_vagas_noturno': 0,
                    'capacidade_vagas_intermediario': 0,
                    'capacidade_vagas_integral': 0,
                    'capacidade_vagas_total': 0,
                    'organizacao_parceira': False,
                    'quantidade_de_funcionarios': 0,
                    'status': 'ATIVA',
                }

                escola, created = Escola.objects.get_or_create(
                    codigo_eol=str(dados.get('codigo') or codigo_eol),
                    defaults=escola_defaults,
                )

                if created:
                    escolas_criadas += 1
                    self.stdout.write(f"    ✓ Criada escola: {escola.nome_oficial} ({escola.codigo_eol})")
                    continue

                changed = False

                if escola.dre_id != dre.id:
                    escola.dre = dre
                    changed = True

                update_fields = []
                for field, new_val in escola_defaults.items():
                    if field == 'dre':
                        continue
                    old_val = getattr(escola, field)
                    if old_val != new_val:
                        setattr(escola, field, new_val)
                        update_fields.append(field)
                        changed = True

                if changed:
                    escola.save(update_fields=['dre'] + update_fields if update_fields else ['dre'])
                    escolas_atualizadas += 1
                    self.stdout.write(f"    ↻ Atualizada escola: {escola.nome_oficial} ({escola.codigo_eol})")
                else:
                    escolas_sem_alteracao += 1
                    self.stdout.write(f"    - Sem alterações: {escola.nome_oficial} ({escola.codigo_eol})")

        self.stdout.write(self.style.SUCCESS(
            f"✅ Escolas: criadas={escolas_criadas}, atualizadas={escolas_atualizadas}, sem_alteracao={escolas_sem_alteracao}"
        )) 