from rest_framework import serializers
from ..models import Dre


class DreSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Dre."""
    class Meta:
        model = Dre
        fields = ['uuid', 'codigo', 'nome', 'sigla']
