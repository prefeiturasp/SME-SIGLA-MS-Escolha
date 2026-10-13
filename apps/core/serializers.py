"""Serializers compartilhados do projeto."""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


class ErroDetalheSerializer(serializers.Serializer):
    """Erro com mensagem única, como o de registro inexistente."""

    detail = serializers.CharField(help_text="Mensagem que descreve o erro.")


class MotivoTokenSerializer(serializers.Serializer):
    """Motivo da rejeição de um token JWT."""

    token_class = serializers.CharField(
        help_text="Classe de token avaliada, por exemplo `AccessToken`."
    )
    token_type = serializers.CharField(
        help_text="Tipo de token avaliado, por exemplo `access`."
    )
    message = serializers.CharField(help_text="Motivo da rejeição.")


class ErroAcessoSerializer(serializers.Serializer):
    """Erro de autenticação ou de permissão."""

    detail = serializers.CharField(help_text="Mensagem que descreve o erro.")
    code = serializers.CharField(
        required=False,
        help_text=(
            "Código do erro. Presente quando o token JWT é rejeitado "
            "(`token_not_valid`) ou quando o usuário do token não existe "
            "neste serviço (`user_not_found`)."
        ),
    )
    messages = MotivoTokenSerializer(
        many=True,
        required=False,
        help_text="Motivos da rejeição do token JWT, quando houver.",
    )


class ErrosValidacaoSerializer(serializers.Serializer):
    """Erros de validação no formato padrão do Django REST Framework."""


class LinksPaginacaoSerializer(serializers.Serializer):
    """Links de navegação entre as páginas da listagem."""

    next = serializers.URLField(
        allow_null=True,
        help_text="URL da próxima página, ou nulo na última página.",
    )
    previous = serializers.URLField(
        allow_null=True,
        help_text="URL da página anterior, ou nulo na primeira página.",
    )


@extend_schema_serializer(many=False)
class PaginaSerializer(serializers.Serializer):
    """Página de uma listagem, com os links agrupados em ``links``."""

    links = LinksPaginacaoSerializer(
        help_text="Links para as páginas vizinhas."
    )
    count = serializers.IntegerField(
        help_text="Total de registros que atendem aos filtros."
    )
    page = serializers.IntegerField(help_text="Número da página retornada.")
    page_size = serializers.IntegerField(
        help_text="Quantidade de registros por página pedida."
    )
