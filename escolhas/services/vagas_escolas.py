import logging
from typing import List, Dict, Any, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import status

from ..models import VagasEscolas, Escola
from ..serializers import VagasEscolasCreateSerializer

logger = logging.getLogger(__name__)


def criar_vagas_em_lote(vagas_data: List[Dict[str, Any]]) -> Tuple[List[VagasEscolas], List[Dict[str, Any]]]:
    """
    Cria múltiplas vagas em lote.
    
    Args:
        vagas_data: Lista de dicionários com os dados das vagas
        
    Returns:
        Tuple contendo:
        - Lista das vagas criadas com sucesso
        - Lista dos erros encontrados durante a criação
        
    Raises:
        ValidationError: Se os dados de entrada forem inválidos
    """
    errors = []
    created_vagas = []
    
    with transaction.atomic():
        for i, vaga_data in enumerate(vagas_data):
            try:
                # Busca a escola pelo código EOL
                codigo_eol = vaga_data.pop('codigo_eol')
                
                try:
                    escola = Escola.objects.get(codigo_eol=codigo_eol)
                except Escola.DoesNotExist:
                    error_msg = f"Escola com código EOL '{codigo_eol}' não encontrada na vaga {i+1}"
                    logger.error(error_msg)
                    errors.append({
                        'vaga_index': i + 1,
                        'codigo_eol': codigo_eol,
                        'error': error_msg
                    })
                    continue
                
                # Cria a vaga
                vaga = VagasEscolas.objects.create(
                    escola=escola,
                    **vaga_data
                )
                created_vagas.append(vaga)
                
            except Exception as e:
                error_msg = f"Erro ao criar vaga {i+1}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    'vaga_index': i + 1,
                    'error': error_msg
                })
                continue
    
    return created_vagas, errors


def processar_criacao_vagas_lote(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Processa a criação de vagas em lote a partir dos dados da requisição.
    
    Args:
        request_data: Dados da requisição contendo a chave 'vagas'
        
    Returns:
        Tuple contendo:
        - Dicionário com os dados da resposta
        - Status HTTP da resposta
    """
    # Valida os dados de entrada
    serializer = VagasEscolasCreateSerializer(data=request_data)
    
    if not serializer.is_valid():
        return {
            'errors': serializer.errors
        }, status.HTTP_400_BAD_REQUEST
    
    # Processa a criação em lote
    vagas_data = serializer.validated_data['vagas']
    created_vagas, errors = criar_vagas_em_lote(vagas_data)
    
    # Prepara resposta
    response_data = {
        'mensagem': f'{len(created_vagas)} vagas criadas com sucesso',
        'vagas_criadas': len(created_vagas),
        'total_processadas': len(vagas_data)
    }
    
    if errors:
        response_data['erros'] = errors
        response_data['vagas_com_erro'] = len(errors)
    
    # Determina status da resposta
    if not created_vagas and errors:
        # Nenhuma vaga criada, apenas erros
        status_code = status.HTTP_400_BAD_REQUEST
    elif errors:
        # Algumas vagas criadas, mas houve erros
        status_code = status.HTTP_207_MULTI_STATUS
    else:
        # Sucesso total
        status_code = status.HTTP_201_CREATED
    
    return response_data, status_code
