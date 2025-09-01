import pytest
from django.core.exceptions import ValidationError
from concursos.models import Cargo, Concurso
import uuid


pytestmark = pytest.mark.django_db


def test_base_model_fields():
    """Testa se o BaseModel tem os campos necessários."""
    # Criar um cargo para testar os campos do BaseModel
    cargo = Cargo.objects.create(nome='Teste')
    
    # Verificar se os campos estão presentes
    assert cargo.uuid is not None
    assert cargo.criado_em is not None
    assert cargo.atualizado_em is not None
    
    # Verificar se o UUID é válido
    assert isinstance(cargo.uuid, uuid.UUID)
    
    # Verificar se as datas são válidas
    from django.utils import timezone
    assert isinstance(cargo.criado_em, timezone.datetime)
    assert isinstance(cargo.atualizado_em, timezone.datetime)


def test_cargo_model_fields():
    """Testa se o modelo Cargo tem todos os campos necessários."""
    # Verificar campos do modelo
    fields = [field.name for field in Cargo._meta.fields]
    expected_fields = ['uuid', 'nome', 'criado_em', 'atualizado_em']
    
    for field in expected_fields:
        assert field in fields


def test_concurso_model_fields():
    """Testa se o modelo Concurso tem todos os campos necessários."""
    # Verificar campos do modelo
    fields = [field.name for field in Concurso._meta.fields]
    expected_fields = ['uuid', 'nome', 'criado_em', 'atualizado_em']
    
    for field in expected_fields:
        assert field in fields
