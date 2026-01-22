from django.db import models
from auditlog.registry import auditlog
from .base import BaseModel


class Parametrizacao(BaseModel):
    """
    Parametriza o uso de tipos de unidade escolar (tipo_ue) no sistema.
    Cada registro representa um tipo_ue único e se ele deve ser utilizado.
    """
    tipo_ue = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Tipo UE")
    usar = models.BooleanField(default=False, verbose_name="Utilizar este tipo de UE")

    class Meta:
        db_table = 'escolhas_parametrizacao'
        verbose_name = 'Parametrização de Tipo UE'
        verbose_name_plural = 'Parametrizações de Tipos UE'
        ordering = ['tipo_ue']

    def __str__(self):
        return f"{self.tipo_ue} ({'usar' if self.usar else 'não usar'})"

    @classmethod
    def sync_from_escolas(cls) -> int:
        """
        Garante que exista um registro para cada tipo_ue distinto em Escola.
        Retorna a quantidade de registros criados.
        """
        from .escola import Escola

        qs = (
            Escola.objects
            .exclude(tipo_ue__isnull=True)
            .exclude(tipo_ue='')
            .order_by('tipo_ue')
            .values_list('tipo_ue', flat=True)
            .distinct()
        )
        tipos_distintos = list(qs)  # deve refletir o total distinto (ex.: 25)
        existentes = set(cls.objects.values_list('tipo_ue', flat=True))

        # Criar novos registros que não existirem ainda
        novos = []
        for tipo in tipos_distintos:
            if tipo in existentes:
                continue
            novos.append(cls(tipo_ue=tipo))
        if novos:
            cls.objects.bulk_create(novos)

        return len(novos)


auditlog.register(Parametrizacao)

