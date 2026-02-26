from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django.db.models import Count

from ..choices import SituacaoChoices, TipoVagaChoices
from ..models import Escolha, VagasEscolas, Escola
from ..serializers import (
    EscolhaSerializer,
    EscolhaSelectSerializer,
    EscolhaListSerializer,
    EscolhaReconvocacaoSerializer,
    EscolhasProdamImportacaoSerializer,
)
from ..services import CandidatoAPIService, ConcursoAPIService
from ..utils import CustomPagination
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EscolhaViewSet(viewsets.ModelViewSet):
    queryset = Escolha.objects.all()
    serializer_class = EscolhaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'candidato_uuid': ['exact'],
        'concurso_uuid': ['exact'],
        'situacao': ['exact', 'in'],
        'vaga_escola__cargo_codigo': ['exact'],
    }
    search_fields = ['situacao', 'tipo_vaga']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Escolha.objects.all()
        if self.action in ['list', 'retrieve', 'busca']:
            qs = qs.select_related(
                'vaga_escola',
                'vaga_escola__escola',
                'vaga_escola__escola__dre',
            ).prefetch_related('historico')
        return qs

    def get_serializer_class(self):
        if self.action in ['list', 'busca']:
            return EscolhaListSerializer
        if self.action == 'select':
            return EscolhaSelectSerializer
        if self.action == 'reconvocacao':
            return EscolhaReconvocacaoSerializer
        return super().get_serializer_class()

    @action(methods=['post'], detail=False, url_path='busca')
    def busca(self, request):
        candidato_ids = request.data.get('candidato_uuid', [])
        if not isinstance(candidato_ids, list):
            return Response(
                {'detail': 'candidato_uuid deve ser uma lista de UUIDs.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().select_related(
            'vaga_escola',
            'vaga_escola__escola',
            'vaga_escola__escola__dre'
        ).filter(candidato_uuid__in=candidato_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='reconvocacao')
    def reconvocacao(self, request):
        """
        Endpoint para buscar escolhas com situação de reconvocação.
        Retorna apenas uuid e candidato_uuid.
        """
        queryset = self.get_queryset().filter(situacao=SituacaoChoices.RECONVOCACAO)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='buscar-candidatos')
    def buscar_candidatos(self, request):
        """
        Busca candidatos no MS-Candidatos por nome, CPF, RG ou registro funcional.
        Query params: nome, cpf, rg, registro_funcional (pelo menos um obrigatório).
        """
        nome = request.query_params.get('nome', '').strip()
        cpf = request.query_params.get('cpf', '').strip()
        rg = request.query_params.get('rg', '').strip()
        registro_funcional = request.query_params.get('registro_funcional', '').strip()

        if not any([nome, cpf, rg, registro_funcional]):
            return Response(
                {'detail': 'Informe pelo menos um parâmetro: nome, cpf, rg ou registro_funcional.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        candidatos = CandidatoAPIService().buscar_candidatos(
            nome=nome or None,
            cpf=cpf or None,
            rg=rg or None,
            registro_funcional=registro_funcional or None,
        )
        if candidatos is None:
            return Response(
                {'detail': 'Erro ao consultar serviço de candidatos.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(candidatos)

    @action(methods=['get'], detail=False, url_path='agrupar-por-cargo')
    def agrupar_por_cargo(self, request):
        """
        Agrupa todas as escolhas por vaga_escola__cargo_codigo e retorna a soma de escolhas por cargo.
        """
        qs = (
            self.get_queryset().filter(situacao=SituacaoChoices.ESCOLHA)
            .values('vaga_escola__cargo_codigo')
            .annotate(total=Count('uuid'))
            .order_by('vaga_escola__cargo_codigo')
        )
        data = {
            str(item['vaga_escola__cargo_codigo']): int(item['total'] or 0)
            for item in qs
        }
        return Response(data)

    @action(methods=['post'], detail=False, url_path='importacao-prodam')
    def importacao_prodam(self, request):
        """
        Endpoint para receber dados de escolhas.
        
        Payload esperado:
        {
            "processo_uuid": "uuid-do-processo",
            "escolhas": [
                {
                    "cpf": "12345678901",
                    "codigo_cargo": "123",
                    "codigo_eol": "456789",
                    "tipo_vaga": "PRECARIA",
                    "situacao": "escolha"
                }
            ]
        }
        """
        # 1. Validar dados de entrada
        serializer = EscolhasProdamImportacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cpfs = [escolha['cpf'] for escolha in serializer.validated_data['escolhas']]
        processo_uuid = serializer.validated_data['processo_uuid'] 
        candidatos = CandidatoAPIService().buscar_candidatos_por_cpfs(cpfs, processo_uuid)
        escolhas = serializer.validated_data['escolhas']
        concurso_uuid = serializer.validated_data['concurso_uuid']
        codigos_eol = list(set([escolha['codigo_eol'].zfill(6) for escolha in escolhas if escolha.get('codigo_eol')]))
        codigos_cargo = list(set([int(escolha['codigo_cargo']) for escolha in escolhas if escolha.get('codigo_cargo')]))
        
        # Criar dict para mapear CPF -> UUID do candidato
        candidatos_dict = {}
        if candidatos:
            for candidato in candidatos:
                cpf_candidato = candidato.get('cpf')
                if cpf_candidato:
                    # Normalizar CPF para comparação (remover máscara)
                    candidatos_dict[cpf_candidato] = candidato.get('uuid')
        
        # Buscar todas as vagas_escolas de uma vez usando a lista de códigos EOL e códigos de cargo
        vagas_escolas_dict = {}
        if codigos_eol and codigos_cargo:
            try:
                vagas_escolas = VagasEscolas.objects.filter(
                    escola__codigo_eol__in=codigos_eol,
                    cargo_codigo__in=codigos_cargo
                ).select_related('escola')
                
                # Criar dict onde chave é (codigo_eol, codigo_cargo) e valor é o objeto VagasEscolas
                for vaga_escola in vagas_escolas:
                    codigo_eol = vaga_escola.escola.codigo_eol
                    codigo_cargo = str(vaga_escola.cargo_codigo)
                    chave = (codigo_eol, codigo_cargo)
                    vagas_escolas_dict[chave] = vaga_escola
                
                logger.info(f'Vagas encontradas: {len(vagas_escolas_dict)} de {len(codigos_eol)} códigos EOL e {len(codigos_cargo)} códigos de cargo')
            except Exception as exc:
                logger.error(f'Erro ao buscar vagas_escolas: {exc}')
        
        # Iterar sobre escolhas e criar registros
        escolhas_criadas = []
        erros = []
        
        for idx, escolha_data in enumerate(escolhas):
            try:
                # Buscar candidato_uuid pelo CPF
                cpf_escolha = escolha_data.get('cpf')
                candidato_uuid = candidatos_dict.get(cpf_escolha)
                
                if not candidato_uuid:
                    erros.append({
                        'index': idx,
                        'cpf': cpf_escolha,
                        'erro': 'Candidato não encontrado'
                    })
                    continue
                
                # Buscar vaga_escola pelo codigo_eol e codigo_cargo
                codigo_eol = escolha_data.get('codigo_eol')
                codigo_cargo = escolha_data.get('codigo_cargo')
                vaga_escola = None
                if codigo_eol and codigo_cargo:
                    codigo_eol_normalizado = str(codigo_eol).zfill(6)
                    codigo_cargo_str = str(codigo_cargo)
                    chave = (codigo_eol_normalizado, codigo_cargo_str)
                    vaga_escola = vagas_escolas_dict.get(chave)
                
                # Mapear situacao
                situacao_map = {
                    'ESCOLHA': SituacaoChoices.ESCOLHA,
                    'NAO-ESCOLHA': SituacaoChoices.NAO_ESCOLHA,
                    'RECONVOCACAO': SituacaoChoices.RECONVOCACAO,
                    'PENDENTE': SituacaoChoices.NAO_ESCOLHA,  # PENDENTE vira NAO_ESCOLHA
                }
                situacao = situacao_map.get(escolha_data.get('situacao', '').upper(), SituacaoChoices.NAO_ESCOLHA)
                
                # Mapear tipo_vaga
                tipo_vaga = None
                tipo_vaga_raw = escolha_data.get('tipo_vaga')
                if tipo_vaga_raw:
                    tipo_vaga_map = {
                        'P': TipoVagaChoices.PRECARIA,
                        'D': TipoVagaChoices.DEFINITIVA,
                    }
                    tipo_vaga = tipo_vaga_map.get(str(tipo_vaga_raw).upper())
                
                # Validar duplicação: verificar se já existe escolha para o mesmo candidato no mesmo concurso
                escolha_existente = Escolha.objects.filter(
                    candidato_uuid=candidato_uuid,
                    concurso_uuid=concurso_uuid
                ).first()
                
                if escolha_existente:
                    logger.warning(
                        f'Escolha duplicada detectada na importação (índice {idx}): '
                        f'CPF={cpf_escolha}, candidato_uuid={candidato_uuid}, '
                        f'concurso_uuid={concurso_uuid}. '
                        f'Escolha existente UUID: {escolha_existente.uuid}'
                    )
                    continue
                
                # Criar registro de Escolha (mesmo que já exista, criar novo registro)
                nova_escolha = Escolha.objects.create(
                    candidato_uuid=candidato_uuid,
                    concurso_uuid=concurso_uuid,
                    situacao=situacao,
                    tipo_vaga=tipo_vaga,
                    vaga_escola=vaga_escola
                )
                
                escolhas_criadas.append({
                    'uuid': str(nova_escolha.uuid),
                    'candidato_uuid': str(candidato_uuid),
                    'situacao': nova_escolha.situacao
                })
            
            except Exception as exc:
                logger.error(f'Erro ao criar escolha {idx}: {exc}', exc_info=True)
                erros.append({
                    'index': idx,
                    'cpf': escolha_data.get('cpf', 'N/A'),
                    'erro': str(exc)
                })
        
        # Retornar resposta
        response_data = {
            'escolhas_criadas': len(escolhas_criadas),
            'escolhas': escolhas_criadas
        }

        if erros:
            response_data['erros'] = erros
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
