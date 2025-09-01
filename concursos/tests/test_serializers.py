import pytest
from concursos.models import Cargo, Concurso
from concursos.serializers import (
    CargoSerializer,
    CargoListSerializer,
    CargoSelectSerializer,
    ConcursoSerializer,
    ConcursoListSerializer,
    ConcursoSelectSerializer
)


pytestmark = pytest.mark.django_db


def test_cargo_serializer_fields(cargo_analista):
    """Testa se o CargoSerializer tem todos os campos necessários."""
    serializer = CargoSerializer(cargo_analista)
    data = serializer.data
    
    assert 'uuid' in data
    assert 'nome' in data
    assert 'criado_em' in data
    assert 'atualizado_em' in data
    
    assert data['nome'] == 'Analista de Sistemas'
    assert data['uuid'] == str(cargo_analista.uuid)

def test_cargo_serializer_read_only_fields():
    """Testa se os campos uuid, criado_em e atualizado_em são somente leitura."""
    data = {
        'uuid': 'invalid-uuid',
        'nome': 'Novo Nome',
        'criado_em': '2024-01-01T00:00:00Z',
        'atualizado_em': '2024-01-01T00:00:00Z'
    }
    
    serializer = CargoSerializer(data=data)
    assert serializer.is_valid()
    
    # Os campos read_only devem ser ignorados
    cargo = serializer.save()
    assert cargo.nome == 'Novo Nome'
    assert str(cargo.uuid) != 'invalid-uuid'

def test_cargo_list_serializer_fields(cargo_analista):
    """Testa se o CargoListSerializer tem apenas os campos necessários para listagem."""
    serializer = CargoListSerializer(cargo_analista)
    data = serializer.data
    
    assert 'uuid' in data
    assert 'nome' in data
    assert 'criado_em' not in data
    assert 'atualizado_em' not in data
    
    assert data['nome'] == 'Analista de Sistemas'
    assert data['uuid'] == str(cargo_analista.uuid)

def test_cargo_select_serializer_fields(cargo_analista):
    """Testa se o CargoSelectSerializer tem o formato correto para selects."""
    serializer = CargoSelectSerializer(cargo_analista)
    data = serializer.data
    
    assert 'value' in data
    assert 'label' in data
    assert 'uuid' not in data
    assert 'nome' not in data
    
    assert data['value'] == str(cargo_analista.uuid)
    assert data['label'] == 'Analista de Sistemas'

def test_cargo_serializer_validation_valid(cargo_data):
    """Testa se a validação do CargoSerializer funciona com dados válidos."""
    serializer = CargoSerializer(data=cargo_data)
    assert serializer.is_valid()

def test_cargo_serializer_validation_empty_nome(cargo_data_invalid):
    """Testa se a validação falha com nome vazio."""
    serializer = CargoSerializer(data=cargo_data_invalid)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors

def test_cargo_serializer_validation_long_nome(cargo_data_long_name):
    """Testa se a validação falha com nome muito longo."""
    serializer = CargoSerializer(data=cargo_data_long_name)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors

def test_cargo_serializer_create(cargo_data):
    """Testa se a criação via serializer funciona."""
    serializer = CargoSerializer(data=cargo_data)
    assert serializer.is_valid()
    
    cargo = serializer.save()
    assert cargo.nome == 'Novo Cargo de Teste'
    assert cargo.uuid is not None
    assert cargo.criado_em is not None
    assert cargo.atualizado_em is not None

def test_cargo_serializer_update(cargo_analista):
    """Testa se a atualização via serializer funciona."""
    data = {'nome': 'Nome Atualizado'}
    serializer = CargoSerializer(cargo_analista, data=data, partial=True)
    assert serializer.is_valid()
    
    cargo = serializer.save()
    assert cargo.nome == 'Nome Atualizado'
    assert cargo.uuid == cargo_analista.uuid  # UUID não deve mudar


def test_concurso_serializer_fields(concurso_analista):
    """Testa se o ConcursoSerializer tem todos os campos necessários."""
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    
    assert 'uuid' in data
    assert 'nome' in data
    assert 'cargos' in data
    assert 'criado_em' in data
    assert 'atualizado_em' in data
    
    assert data['nome'] == 'Concurso de Analista'
    assert data['uuid'] == str(concurso_analista.uuid)
    assert len(data['cargos']) == 1
    assert data['cargos'][0]['nome'] == 'Analista de Sistemas'

def test_concurso_serializer_create(concurso_data):
    """Testa se o método create do ConcursoSerializer funciona corretamente."""
    serializer = ConcursoSerializer(data=concurso_data)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Novo Concurso de Teste'
    assert concurso.cargos.count() == 1

def test_concurso_serializer_create_without_cargos(concurso_data_no_cargos):
    """Testa se é possível criar um concurso sem cargos."""
    serializer = ConcursoSerializer(data=concurso_data_no_cargos)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso Sem Cargos'
    assert concurso.cargos.count() == 0

def test_concurso_serializer_create_with_invalid_cargo_ids(concurso_data_invalid_cargo_ids):
    """Testa se a criação com IDs de cargo inválidos funciona (ignora IDs inválidos)."""
    serializer = ConcursoSerializer(data=concurso_data_invalid_cargo_ids)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso com Cargo Inválido'
    assert concurso.cargos.count() == 0

def test_concurso_serializer_create_with_multiple_cargos(concurso_data_multiple_cargos):
    """Testa se é possível criar um concurso com múltiplos cargos."""
    serializer = ConcursoSerializer(data=concurso_data_multiple_cargos)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso com Múltiplos Cargos'
    assert concurso.cargos.count() == 2

def test_concurso_serializer_update(concurso_analista, cargo_desenvolvedor):
    """Testa se o método update do ConcursoSerializer funciona corretamente."""
    data = {
        'nome': 'Concurso Atualizado',
        'cargos_ids': [str(cargo_desenvolvedor.uuid)]
    }
    
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso Atualizado'
    assert concurso.cargos.count() == 1
    assert cargo_desenvolvedor in concurso.cargos.all()

def test_concurso_serializer_update_clear_cargos(concurso_analista):
    """Testa se é possível limpar todos os cargos de um concurso."""
    data = {'cargos_ids': []}
    
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.cargos.count() == 0

def test_concurso_serializer_validation_valid(concurso_data):
    """Testa se a validação funciona com dados válidos."""
    serializer = ConcursoSerializer(data=concurso_data)
    assert serializer.is_valid()

def test_concurso_serializer_validation_empty_nome(concurso_data_invalid):
    """Testa se a validação falha com nome vazio."""
    serializer = ConcursoSerializer(data=concurso_data_invalid)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors

def test_concurso_serializer_validation_long_nome():
    """Testa se a validação falha com nome muito longo."""
    data = {'nome': 'A' * 201}  # Mais que max_length=200
    serializer = ConcursoSerializer(data=data)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors

def test_concurso_list_serializer_fields(concurso_analista):
    """Testa se o ConcursoListSerializer tem apenas os campos necessários para listagem."""
    serializer = ConcursoListSerializer(concurso_analista)
    data = serializer.data
    
    assert 'uuid' in data
    assert 'nome' in data
    assert 'cargos' in data
    assert 'criado_em' not in data
    assert 'atualizado_em' not in data
    
    assert data['nome'] == 'Concurso de Analista'
    assert data['uuid'] == str(concurso_analista.uuid)
    assert len(data['cargos']) == 1

def test_concurso_select_serializer_fields(concurso_analista):
    """Testa se o ConcursoSelectSerializer tem o formato correto para selects."""
    serializer = ConcursoSelectSerializer(concurso_analista)
    data = serializer.data
    
    assert 'value' in data
    assert 'label' in data
    assert 'cargos' in data
    assert 'uuid' not in data
    assert 'nome' not in data
    
    assert data['value'] == str(concurso_analista.uuid)
    assert data['label'] == 'Concurso de Analista'
    assert len(data['cargos']) == 1
    assert data['cargos'][0]['value'] == str(concurso_analista.cargos.first().uuid)
    assert data['cargos'][0]['label'] == 'Analista de Sistemas'

def test_concurso_serializer_cargos_ids_field(concurso_analista):
    """Testa se o campo cargos_ids é write_only e não aparece na serialização."""
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    
    assert 'cargos_ids' not in data
    
    # Mas deve aceitar na criação/atualização
    data = {
        'nome': 'Teste',
        'cargos_ids': [str(concurso_analista.cargos.first().uuid)]
    }
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()

def test_concurso_serializer_nested_cargos(concurso_analista, cargo_desenvolvedor):
    """Testa se os cargos aninhados são serializados corretamente."""
    # Adicionar mais um cargo
    concurso_analista.cargos.add(cargo_desenvolvedor)
    
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    
    assert len(data['cargos']) == 2
    cargo_nomes = [cargo['nome'] for cargo in data['cargos']]
    assert 'Analista de Sistemas' in cargo_nomes
    assert 'Desenvolvedor Backend' in cargo_nomes

def test_concurso_serializer_partial_update(concurso_analista):
    """Testa se a atualização parcial funciona corretamente."""
    # Atualizar apenas o nome
    data = {'nome': 'Nome Atualizado'}
    
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Nome Atualizado'
    # Os cargos devem ser mantidos
    assert concurso.cargos.count() == 1

def test_concurso_serializer_create_with_empty_cargos_ids():
    """Testa se a criação com cargos_ids vazio funciona."""
    data = {
        'nome': 'Concurso Vazio',
        'cargos_ids': []
    }
    
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso Vazio'
    assert concurso.cargos.count() == 0

def test_concurso_serializer_update_with_none_cargos_ids(concurso_analista):
    """Testa se a atualização com cargos_ids None mantém os cargos existentes."""
    data = {'nome': 'Nome Atualizado'}
    
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Nome Atualizado'
    # Os cargos devem ser mantidos
    assert concurso.cargos.count() == 1

def test_concurso_serializer_invalid_uuid_format():
    """Testa se a validação falha com formato de UUID inválido."""
    data = {
        'nome': 'Concurso Teste',
        'cargos_ids': ['invalid-uuid-format']
    }
    
    serializer = ConcursoSerializer(data=data)
    assert not serializer.is_valid()
    assert 'cargos_ids' in serializer.errors

def test_concurso_serializer_mixed_valid_invalid_cargos(cargo_analista):
    """Testa se a criação com cargos válidos e inválidos funciona."""
    import uuid
    fake_uuid = uuid.uuid4()
    
    data = {
        'nome': 'Concurso Misto',
        'cargos_ids': [str(cargo_analista.uuid), str(fake_uuid)]
    }
    
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()
    
    concurso = serializer.save()
    assert concurso.nome == 'Concurso Misto'
    # Deve associar apenas o cargo válido
    assert concurso.cargos.count() == 1
    assert cargo_analista in concurso.cargos.all()
