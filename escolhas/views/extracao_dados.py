"""ViewSet de extração de dados de escolhas."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers import ExtracaoDadosSerializer
from ..services import montar_extracao_dados


class ExtracaoDadosViewSet(viewsets.ViewSet):
    """
    Indicadores de escolhas para extração de dados.

    POST /extracao-dados/
    Body: {concurso_uuid?, filtros?: [{ano, processo_uuids?}]}
    Sem `filtros`: retorna a chave "total" agregando todas as escolhas.
    """

    permission_classes = [AllowAny]

    def create(self, request):
        serializer = ExtracaoDadosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        resultado = montar_extracao_dados(
            concurso_uuid=dados.get("concurso_uuid"),
            filtros=dados["filtros"],
        )
        return Response(resultado)
