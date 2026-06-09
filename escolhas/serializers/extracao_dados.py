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

    - ``concurso_uuid`` (opcional): concurso cujas escolhas serão contadas.
      Ausente → agrega escolhas de todos os concursos.
    - ``filtros`` (opcional): lista de ``{ano}``; cada ano filtra as escolhas
      pelo ano de criação (``criado_em``). Ausente (ou vazia) → o resultado traz
      uma única chave agregada ``"total"`` sem quebra por ano.
    """

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    filtros = ExtracaoDadosFiltroSerializer(
        many=True, required=False, default=list
    )
