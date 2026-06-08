from rest_framework import serializers


class ExtracaoDadosFiltroSerializer(serializers.Serializer):
    """Filtro de um ano.

    ``processo_uuids`` (opcional) é usado apenas para somar as vagas por DRE,
    pois ``VagasEscolas`` só se liga ao processo via ``lote.processo_uuid``.
    """

    ano = serializers.IntegerField()
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Payload do endpoint de extração de dados de escolhas.

    - ``concurso_uuid``: concurso cujas escolhas serão contadas.
    - ``filtros``: lista de ``{ano}``; cada ano filtra as escolhas pelo
      ano de criação (``criado_em``).
    """

    concurso_uuid = serializers.UUIDField()
    filtros = ExtracaoDadosFiltroSerializer(many=True, allow_empty=False)
