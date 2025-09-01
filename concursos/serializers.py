from rest_framework import serializers
from .models import Cargo, Concurso


class CargoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Cargo.
    """
    class Meta:
        model = Cargo
        fields = ['uuid', 'nome', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']


class CargoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de cargos.
    """
    class Meta:
        model = Cargo
        fields = ['uuid', 'nome']


class CargoSelectSerializer(serializers.ModelSerializer):
    """
    Serializer para selects/dropdowns no frontend.
    """
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='nome')
    
    class Meta:
        model = Cargo
        fields = ['value', 'label']


class ConcursoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Concurso.
    """
    cargos = CargoListSerializer(many=True, read_only=True)
    cargos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Concurso
        fields = ['uuid', 'nome', 'cargos', 'cargos_ids', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']
    
    def create(self, validated_data):
        cargos_ids = validated_data.pop('cargos_ids', [])
        concurso = Concurso.objects.create(**validated_data)
        
        if cargos_ids:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            concurso.cargos.set(cargos)
        
        return concurso
    
    def update(self, instance, validated_data):
        cargos_ids = validated_data.pop('cargos_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if cargos_ids is not None:
            cargos = Cargo.objects.filter(uuid__in=cargos_ids)
            instance.cargos.set(cargos)
        
        return instance


class ConcursoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de concursos.
    """
    cargos = CargoListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Concurso
        fields = ['uuid', 'nome', 'cargos']


class ConcursoSelectSerializer(serializers.ModelSerializer):
    """
    Serializer para selects/dropdowns no frontend.
    """
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='nome')
    cargos = CargoSelectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Concurso
        fields = ['value', 'label', 'cargos']
