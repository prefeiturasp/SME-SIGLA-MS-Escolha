"""Comando para atualizar o campo codigo_integracao das escolas a partir da.

SME.
1. Busca DREs na API.
2. Para cada DRE, chama GET /api/DREs/{dreCodigo}/unidades/codigo-integracao.
3. Para cada unidade retornada, localiza a escola pelo codigo_eol (codigoUe) e
atualiza codigo_integracao.
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from escolhas.models import Escola
from escolhas.services.sme_integration import (
    buscar_dres_de_smeintegracao,
    buscar_unidades_codigo_integracao_por_dre,
)


class Command(BaseCommand):
    """Representa Command."""

    help = (
        "Atualiza codigo_integracao das escolas: busca DREs na SME, "
        "para cada DRE obtém unidades (codigo-integracao) e atualiza "
        "as escolas pelo codigo_eol."
    )

    def handle(self, *args: Any, **options: Any) -> None:
        """Roda a lógica principal do comando."""
        self.stdout.write(
            self.style.SUCCESS("Buscando DREs na SME Integracao...")
        )
        try:
            dres = buscar_dres_de_smeintegracao()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Falha ao buscar DREs: {exc}"))
            return
        self.stdout.write(f"Encontradas {len(dres)} DREs no serviço externo.")
        atualizadas = 0
        nao_encontradas = 0
        erros = 0
        with transaction.atomic():
            for item in dres:
                codigo_dre = item["codigo"]
                item.get("nome", "")
                sigla_dre = item.get("sigla", "")
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f"Consultando unidades da DRE {sigla_dre} ({codigo_dre})..."  # noqa: E501
                    )
                )
                try:
                    unidades = buscar_unidades_codigo_integracao_por_dre(
                        codigo_dre
                    )
                except Exception as exc:
                    self.stderr.write(
                        self.style.ERROR(
                            f"  Falha ao buscar unidades da DRE {codigo_dre}: {exc}"  # noqa: E501
                        )
                    )
                    erros += 1
                    continue
                self.stdout.write(f"  Encontradas {len(unidades)} unidades.")
                for u in unidades:
                    codigo_ue = u.get("codigoUe")
                    codigo_integracao = u.get("codigoIntegracao") or ""
                    try:
                        escola = Escola.objects.get(codigo_eol=codigo_ue)
                    except Escola.DoesNotExist:
                        nao_encontradas += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Escola não encontrada no BD: codigo_eol={codigo_ue}"  # noqa: E501
                            )
                        )
                        continue
                    if (
                        codigo_integracao
                        and codigo_integracao != ""
                        and (escola.codigo_integracao != codigo_integracao)
                    ):
                        escola.codigo_integracao = codigo_integracao
                        escola.save(update_fields=["codigo_integracao"])
                        atualizadas += 1
                        self.stdout.write(
                            f"  ↻ Atualizada: {escola.nome_oficial} ({codigo_ue}) -> {codigo_integracao}"  # noqa: E501
                        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: atualizadas={atualizadas}, não encontradas={nao_encontradas}, erros_dre={erros}"  # noqa: E501
            )
        )
