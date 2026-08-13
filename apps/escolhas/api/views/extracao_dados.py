"""ViewSet de extração de dados de escolhas."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from escolhas.serializers import ExtracaoDadosSerializer
from escolhas.services import montar_extracao_dados


class ExtracaoDadosViewSet(viewsets.ViewSet):
    """ViewSet de escolhas para extração de dados.

    POST /extracao-dados/
    Body: {concurso_uuid?, filtros?: [{ano, processo_uuids?}]}
    Com ``filtros``: dados por ano e metadados ``concurso_uuid``/``filtros``.
    Sem ``filtros``: agregado na raiz.
    """

    permission_classes = [AllowAny]

    def create(self, request: Request) -> Response:
        """Recebe filtros e retorna a Extração de Dados agregada."""
        serializer = ExtracaoDadosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        resultado = montar_extracao_dados(
            concurso_uuid=dados.get("concurso_uuid"),
            filtros=dados["filtros"],
        )
        return Response(resultado)
