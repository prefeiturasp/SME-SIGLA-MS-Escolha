"""Módulo signals."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from escolhas.constants import SituacaoChoices, TipoVagaChoices
from escolhas.models import Escolha
from escolhas.repository import EscolhaRepository
from vagas_escolas.repository import VagasEscolasRepository

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Escolha)
def escolha_pre_save(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Captura o estado anterior de situacao antes de salvar."""
    if instance.pk:
        try:
            old_instance = EscolhaRepository.obter_por_pk(instance.pk)
            instance._situacao_anterior = old_instance.situacao
        except Escolha.DoesNotExist:
            instance._situacao_anterior = None
    else:
        instance._situacao_anterior = None


@receiver(post_save, sender=Escolha)
def escolha_post_save(
    sender: Any, instance: Any, created: Any, **kwargs: Any
) -> None:
    """Cria histórico de escolha e atualiza vagas após salvar."""
    situacao_anterior = getattr(instance, "_situacao_anterior", None)
    situacao_atual = instance.situacao
    if created:
        try:
            EscolhaRepository.criar_historico(
                escolha=instance,
                situacao_anterior=None,
                situacao_nova=situacao_atual,
            )
            logger.info(
                "Histórico criado para nova escolha %s: (novo) -> %s",
                instance.uuid,
                situacao_atual,
            )
        except Exception as exc:
            logger.error(
                "Erro ao criar histórico para nova escolha %s: %s",
                instance.uuid,
                exc,
                exc_info=True,
            )
        if (
            situacao_atual == SituacaoChoices.ESCOLHA
            and instance.vaga_escola
            and instance.tipo_vaga
        ):
            try:
                vaga_escola = instance.vaga_escola
                if instance.tipo_vaga == TipoVagaChoices.DEFINITIVA:
                    VagasEscolasRepository.decrementar_definitivas_restantes(
                        vaga_escola.pk
                    )
                    logger.info(
                        "Vaga definitiva decrementada para escolha %s. "
                        "VagaEscola: %s. Novo valor: %s",
                        instance.uuid,
                        vaga_escola.uuid,
                        vaga_escola.vagas_definitivas_restantes - 1,
                    )
                elif instance.tipo_vaga == TipoVagaChoices.PRECARIA:
                    VagasEscolasRepository.decrementar_precarias_restantes(
                        vaga_escola.pk
                    )
                    logger.info(
                        "Vaga precária decrementada para escolha %s. "
                        "VagaEscola: %s. Novo valor: %s",
                        instance.uuid,
                        vaga_escola.uuid,
                        vaga_escola.vagas_precarias_restantes - 1,
                    )
            except Exception as exc:
                logger.error(
                    "Erro ao atualizar vagas restantes para escolha %s: %s",
                    instance.uuid,
                    exc,
                    exc_info=True,
                )
    elif situacao_anterior is not None and situacao_anterior != situacao_atual:
        try:
            EscolhaRepository.criar_historico(
                escolha=instance,
                situacao_anterior=situacao_anterior,
                situacao_nova=situacao_atual,
            )
            logger.info(
                "Histórico criado para escolha %s: %s -> %s",
                instance.uuid,
                situacao_anterior,
                situacao_atual,
            )
        except Exception as exc:
            logger.error(
                f"Erro ao criar histórico para escolha {instance.uuid}: {exc}",
                exc_info=True,
            )
