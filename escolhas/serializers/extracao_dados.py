from rest_framework import serializers


class ExtracaoDadosFiltroSerializer(serializers.Serializer):
    """Serializer de filtro por ano para extração de dados de escolhas."""

    ano = serializers.IntegerField()
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Serializer de escolhas para extração de dados."""

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    filtros = ExtracaoDadosFiltroSerializer(
        many=True, required=False, default=list
    )
