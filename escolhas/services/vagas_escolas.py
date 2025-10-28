from gzip import BadGzipFile
import logging
from typing import List, Dict, Any, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError, BadRequest
from rest_framework import status

from ..models import VagasEscolas, Escola, VagasEscolasLote
from ..serializers import VagasEscolasCreateSerializer

logger = logging.getLogger(__name__)


def criar_vagas_em_lote(vagas_data: List[Dict[str, Any]], lote: VagasEscolasLote) -> Tuple[List[VagasEscolas], List[Dict[str, Any]]]:
    """
    Cria múltiplas vagas em lote.
    """
    errors = []
    created_vagas = []
    
    for i, vaga_data in enumerate(vagas_data):
        try:
            codigo_eol = vaga_data.pop('codigo_eol')
            codigo_eol = codigo_eol.zfill(6)
            try:
                escola = Escola.objects.get(codigo_eol=codigo_eol)
            except Escola.DoesNotExist:
                error_msg = f"Escola com código EOL '{codigo_eol}' não encontrada na vaga {i+1}"
                logger.error(error_msg)
                errors.append({'vaga_index': i + 1, 'codigo_eol': codigo_eol, 'error': error_msg})
                continue
            vaga = VagasEscolas.objects.create(
                escola=escola,
                lote=lote,
                **vaga_data
            )
            created_vagas.append(vaga)
        except Exception as e:
            error_msg = f"Erro ao criar vaga {i+1}: {str(e)}"
            logger.error(error_msg)
            errors.append({'vaga_index': i + 1, 'error': error_msg})
            continue

    return created_vagas, errors


def processar_criacao_vagas_lote(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Processa a criação de vagas em lote a partir dos dados da requisição.
    """
    serializer = VagasEscolasCreateSerializer(data=request_data)

    if not serializer.is_valid():
        return {'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST
    processo_uuid = serializer.validated_data['processo_uuid']
    processo_nome = serializer.validated_data.get('processo_nome', '')
    vagas_data = serializer.validated_data['vagas']

    with transaction.atomic():
        lote = VagasEscolasLote.objects.create(processo_uuid=processo_uuid, processo_nome=processo_nome)
        created_vagas, errors = criar_vagas_em_lote(vagas_data, lote)

    response_data = {
        'mensagem': f'{len(created_vagas)} vagas criadas com sucesso',
        'vagas_criadas': len(created_vagas),
        'total_processadas': len(vagas_data),
        'lote_uuid': str(lote.uuid),
        'processo_uuid': str(processo_uuid),
    }

    if errors:
        response_data['erros'] = errors
        response_data['vagas_com_erro'] = len(errors)

    if not created_vagas and errors:
        status_code = status.HTTP_400_BAD_REQUEST
    elif errors:
        status_code = status.HTTP_207_MULTI_STATUS
    else:
        status_code = status.HTTP_201_CREATED

    return response_data, status_code


def atualizar_vagas_utilizadas_por_processo(
    vagas: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Atualiza campos *_utilizadas de VagasEscolas diretamente por UUID das vagas.

    Args:
        vagas: lista de dicts com keys: uuid, vagas_precarias_utilizadas?, vagas_definitivas_utilizadas?
    Returns:
        dict com listas de atualizados e não encontrados
    """
    from ..models import VagasEscolas  # import local para evitar ciclos

    uuid_to_item = {str(item['uuid']): item for item in vagas}
    vagas_escolas = VagasEscolas.objects.filter(uuid__in=list(uuid_to_item.keys()))

    encontrados = set()
    atualizados = []
    for vaga in vagas_escolas:
        encontrados.add(str(vaga.uuid))
        item = uuid_to_item.get(str(vaga.uuid))
        updates = {}
        if 'foi_utilizada' in item:
            vaga.foi_utilizada = item['foi_utilizada']
            vaga.esta_checada = True if vaga.foi_utilizada else False
            updates['foi_utilizada'] = item['foi_utilizada']
            updates['esta_checada'] = True if vaga.foi_utilizada else False
        if 'vagas_precarias_utilizadas' in item:
            vaga.vagas_precarias_utilizadas = item['vagas_precarias_utilizadas']
            updates['vagas_precarias_utilizadas'] = item['vagas_precarias_utilizadas']
        if 'vagas_definitivas_utilizadas' in item:
            vaga.vagas_definitivas_utilizadas = item['vagas_definitivas_utilizadas']
            updates['vagas_definitivas_utilizadas'] = item['vagas_definitivas_utilizadas']
        if updates:
            vaga.save(update_fields=list(updates.keys()))
            atualizados.append(str(vaga.uuid))

    nao_encontrados = [uid for uid in uuid_to_item.keys() if uid not in encontrados]

    return {
        'atualizados': atualizados,
        'nao_encontrados': nao_encontrados,
        'total': len(atualizados),
    }


def adicionar_vagas_ao_lote_por_processo(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Adiciona novas vagas a um lote existente identificado por processo_uuid.

    Espera o mesmo payload do create:
    {
      "processo_uuid": "...",
      "processo_nome": "opcional",
      "vagas": [ {...}, ... ]
    }
    Retorna (response_dict, http_status_code)
    """
    serializer = VagasEscolasCreateSerializer(data=request_data)
    if not serializer.is_valid():
        return {'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST

    processo_uuid = serializer.validated_data['processo_uuid']
    processo_nome = serializer.validated_data.get('processo_nome', '')
    vagas_data = serializer.validated_data['vagas']

    lote = VagasEscolasLote.objects.filter(processo_uuid=processo_uuid).order_by('-criado_em').first()
    if not lote:
        return {'detail': 'Lote não encontrado para o processo informado'}, status.HTTP_404_NOT_FOUND

    criadas, erros = criar_vagas_em_lote(vagas_data, lote)

    resposta = {
        'mensagem': f'{len(criadas)} vagas adicionadas ao lote',
        'vagas_criadas': len(criadas),
        'total_processadas': len(vagas_data),
        'lote_uuid': str(lote.uuid),
        'processo_uuid': str(processo_uuid),
    }
    if erros:
        resposta['erros'] = erros
        resposta['vagas_com_erro'] = len(erros)
        return resposta, status.HTTP_207_MULTI_STATUS
    return resposta, status.HTTP_201_CREATED
