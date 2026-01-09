import logging
from django.db.models.signals import pre_save, post_save
from django.db.models import F
from django.dispatch import receiver
from .models import Escolha, HistoricoEscolha, VagasEscolas
from .choices import SituacaoChoices, TipoVagaChoices

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Escolha)
def escolha_pre_save(sender, instance, **kwargs):
    """
    Signal que captura o estado anterior do campo situacao antes de salvar.
    Armazena a situação anterior no objeto para uso no post_save.
    """
    if instance.pk:
        try:
            # Busca a instância anterior no banco para capturar a situação anterior
            old_instance = Escolha.objects.get(pk=instance.pk)
            # Armazena o valor anterior no objeto para uso no post_save
            instance._situacao_anterior = old_instance.situacao
        except Escolha.DoesNotExist:
            # Se não encontrar (caso raro), assume que não há situação anterior
            instance._situacao_anterior = None
    else:
        # Se é um novo registro (POST), não há situação anterior
        instance._situacao_anterior = None


@receiver(post_save, sender=Escolha)
def escolha_post_save(sender, instance, created, **kwargs):
    """
    Signal que cria um registro de histórico de escolhas e atualiza vagas das escolas.
    
    Cria histórico nos seguintes casos:
    - POST (criação): sempre cria histórico com situacao_anterior=None
    - PATCH (edição/reconvocacao): cria histórico quando a situação mudou
    
    Atualiza vagas restantes quando:
    - POST (criação) com situacao='escolha' e vaga_escola e tipo_vaga presentes
    """
    situacao_anterior = getattr(instance, '_situacao_anterior', None)
    situacao_atual = instance.situacao
    
    # Cria histórico se:
    # 1. É um novo registro (POST) - sempre cria histórico
    # 2. É uma atualização (PATCH) e a situação mudou
    if created:
        # POST: sempre cria histórico para nova escolha
        try:
            HistoricoEscolha.objects.create(
                escolha=instance,
                situacao_anterior=None,
                situacao_nova=situacao_atual,
            )
            logger.info(
                f"Histórico criado para nova escolha {instance.uuid}: "
                f"(novo) -> {situacao_atual}"
            )
        except Exception as exc:
            logger.error(
                f"Erro ao criar histórico para nova escolha {instance.uuid}: {exc}",
                exc_info=True
            )
        
        # Atualiza vagas restantes quando uma escolha é criada
        if (situacao_atual == SituacaoChoices.ESCOLHA and 
            instance.vaga_escola and 
            instance.tipo_vaga):
            try:
                vaga_escola = instance.vaga_escola
                
                # Decrementa o campo correto baseado no tipo de vaga
                if instance.tipo_vaga == TipoVagaChoices.DEFINITIVA:
                    VagasEscolas.objects.filter(pk=vaga_escola.pk).update(
                        vagas_definitivas_restantes=F('vagas_definitivas_restantes') - 1
                    )
                    logger.info(
                        f"Vaga definitiva decrementada para escolha {instance.uuid}. "
                        f"VagaEscola: {vaga_escola.uuid}. "
                        f"Novo valor: {vaga_escola.vagas_definitivas_restantes - 1}"
                    )
                elif instance.tipo_vaga == TipoVagaChoices.PRECARIA:
                    VagasEscolas.objects.filter(pk=vaga_escola.pk).update(
                        vagas_precarias_restantes=F('vagas_precarias_restantes') - 1
                    )
                    logger.info(
                        f"Vaga precária decrementada para escolha {instance.uuid}. "
                        f"VagaEscola: {vaga_escola.uuid}. "
                        f"Novo valor: {vaga_escola.vagas_precarias_restantes - 1}"
                    )
            except Exception as exc:
                logger.error(
                    f"Erro ao atualizar vagas restantes para escolha {instance.uuid}: {exc}",
                    exc_info=True
                )
    elif situacao_anterior is not None and situacao_anterior != situacao_atual:
        # PATCH: cria histórico apenas quando a situação mudou (reconvocação)
        try:
            HistoricoEscolha.objects.create(
                escolha=instance,
                situacao_anterior=situacao_anterior,
                situacao_nova=situacao_atual,
            )
            logger.info(
                f"Histórico criado para escolha {instance.uuid}: "
                f"{situacao_anterior} -> {situacao_atual}"
            )
        except Exception as exc:
            logger.error(
                f"Erro ao criar histórico para escolha {instance.uuid}: {exc}",
                exc_info=True
            )

