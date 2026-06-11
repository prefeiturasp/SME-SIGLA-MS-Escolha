"""Módulo signals."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models import F
from django.db.models.functions import Greatest
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .choices import SituacaoChoices, TipoVagaChoices
from .models import Escolha, HistoricoEscolha, VagasEscolas

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Escolha)
def escolha_pre_save(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Captura o estado anterior de situacao antes de salvar.

    Args:
        sender: Sender.
        instance: Instância do modelo em processamento.
        **kwargs: Argumentos nomeados repassados ao comando.

    Returns:
        Nenhum valor; persiste alterações no banco.
    """
    if instance.pk:
        try:
            old_instance = Escolha.objects.get(pk=instance.pk)
            instance._situacao_anterior = old_instance.situacao
        except Escolha.DoesNotExist:
            instance._situacao_anterior = None
    else:
        instance._situacao_anterior = None


@receiver(post_save, sender=Escolha)
def escolha_post_save(
    sender: Any, instance: Any, created: Any, **kwargs: Any
) -> None:
    """Cria histórico de escolha e atualiza vagas após salvar.

    Args:
        sender: Sender.
        instance: Instância do modelo em processamento.
        created: Created.
        **kwargs: Argumentos nomeados repassados ao comando.

    Returns:
        Nenhum valor; persiste alterações no banco.
    """
    situacao_anterior = getattr(instance, "_situacao_anterior", None)
    situacao_atual = instance.situacao
    if created:
        try:
            HistoricoEscolha.objects.create(
                escolha=instance,
                situacao_anterior=None,
                situacao_nova=situacao_atual,
            )
            logger.info(
                f"Histórico criado para nova escolha {instance.uuid}: (novo) -> {situacao_atual}"  # noqa: E501
            )
        except Exception as exc:
            logger.error(
                f"Erro ao criar histórico para nova escolha {instance.uuid}: {exc}",  # noqa: E501
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
                    VagasEscolas.objects.filter(pk=vaga_escola.pk).update(
                        vagas_definitivas_restantes=Greatest(
                            0, F("vagas_definitivas_restantes") - 1
                        )
                    )
                    logger.info(
                        f"Vaga definitiva decrementada para escolha {instance.uuid}. VagaEscola: {vaga_escola.uuid}. Novo valor: {vaga_escola.vagas_definitivas_restantes - 1}"  # noqa: E501
                    )
                elif instance.tipo_vaga == TipoVagaChoices.PRECARIA:
                    VagasEscolas.objects.filter(pk=vaga_escola.pk).update(
                        vagas_precarias_restantes=Greatest(
                            0, F("vagas_precarias_restantes") - 1
                        )
                    )
                    logger.info(
                        f"Vaga precária decrementada para escolha {instance.uuid}. VagaEscola: {vaga_escola.uuid}. Novo valor: {vaga_escola.vagas_precarias_restantes - 1}"  # noqa: E501
                    )
            except Exception as exc:
                logger.error(
                    f"Erro ao atualizar vagas restantes para escolha {instance.uuid}: {exc}",  # noqa: E501
                    exc_info=True,
                )
    elif situacao_anterior is not None and situacao_anterior != situacao_atual:
        try:
            HistoricoEscolha.objects.create(
                escolha=instance,
                situacao_anterior=situacao_anterior,
                situacao_nova=situacao_atual,
            )
            logger.info(
                f"Histórico criado para escolha {instance.uuid}: {situacao_anterior} -> {situacao_atual}"  # noqa: E501
            )
        except Exception as exc:
            logger.error(
                f"Erro ao criar histórico para escolha {instance.uuid}: {exc}",
                exc_info=True,
            )
