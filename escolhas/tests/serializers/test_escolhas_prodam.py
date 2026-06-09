"""Testes unitários para serializers de escolhas Prodam."""
from __future__ import annotations
from typing import Any
import uuid
import pytest
from rest_framework.exceptions import ValidationError
from escolhas.serializers.escolhas_prodam import EscolhaProdamItemSerializer, EscolhasProdamImportacaoSerializer

class TestEscolhaProdamItemSerializer:
    """Testes para EscolhaProdamItemSerializer."""

    def test_serializer_valido_com_todos_campos(self) -> None:
        """Testa serializer válido com todos os campos."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'codigo_eol': '456789', 'tipo_vaga': 'P', 'situacao': 'ESCOLHA'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['cpf'] == '12345678901'
        assert serializer.validated_data['codigo_cargo'] == '123'
        assert serializer.validated_data['codigo_eol'] == '456789'
        assert serializer.validated_data['tipo_vaga'] == 'P'
        assert serializer.validated_data['situacao'] == 'ESCOLHA'

    def test_serializer_valido_apenas_campos_obrigatorios(self) -> None:
        """Testa serializer válido apenas com campos obrigatórios."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['cpf'] == '12345678901'
        assert serializer.validated_data['codigo_cargo'] == '123'
        assert serializer.validated_data['situacao'] == 'ESCOLHA'
        assert serializer.validated_data.get('codigo_eol') is None or serializer.validated_data.get('codigo_eol') == ''
        assert serializer.validated_data.get('tipo_vaga') is None or serializer.validated_data.get('tipo_vaga') == ''

    def test_serializer_invalido_sem_cpf(self) -> None:
        """Testa serializer inválido sem CPF."""
        data = {'codigo_cargo': '123', 'situacao': 'ESCOLHA'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert not serializer.is_valid()
        assert 'cpf' in serializer.errors

    def test_serializer_invalido_sem_codigo_cargo(self) -> None:
        """Testa serializer inválido sem codigo_cargo."""
        data = {'cpf': '12345678901', 'situacao': 'ESCOLHA'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert not serializer.is_valid()
        assert 'codigo_cargo' in serializer.errors

    def test_serializer_invalido_sem_situacao(self) -> None:
        """Testa serializer inválido sem situacao."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert not serializer.is_valid()
        assert 'situacao' in serializer.errors

    def test_serializer_aceita_codigo_eol_vazio(self) -> None:
        """Testa que serializer aceita codigo_eol vazio."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA', 'codigo_eol': ''}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_aceita_tipo_vaga_vazio(self) -> None:
        """Testa que serializer aceita tipo_vaga vazio."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA', 'tipo_vaga': ''}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_aceita_codigo_eol_nulo(self) -> None:
        """Testa que serializer aceita codigo_eol nulo."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA', 'codigo_eol': None}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_aceita_tipo_vaga_nulo(self) -> None:
        """Testa que serializer aceita tipo_vaga nulo."""
        data = {'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA', 'tipo_vaga': None}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_cpf_max_length(self) -> None:
        """Testa que serializer valida max_length do CPF."""
        data = {'cpf': '1' * 15, 'codigo_cargo': '123', 'situacao': 'ESCOLHA'}
        serializer = EscolhaProdamItemSerializer(data=data)
        assert not serializer.is_valid()
        assert 'cpf' in serializer.errors

class TestEscolhasProdamImportacaoSerializer:
    """Testes para EscolhasProdamImportacaoSerializer."""

    def test_serializer_valido(self) -> None:
        """Testa serializer válido."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123', 'codigo_eol': '456789', 'tipo_vaga': 'P', 'situacao': 'ESCOLHA'}, {'cpf': '98765432100', 'codigo_cargo': '456', 'situacao': 'NAO-ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['concurso_uuid'] == concurso_uuid
        assert serializer.validated_data['processo_uuid'] == processo_uuid
        assert len(serializer.validated_data['escolhas']) == 2

    def test_serializer_invalido_sem_concurso_uuid(self) -> None:
        """Testa serializer inválido sem concurso_uuid."""
        processo_uuid = uuid.uuid4()
        data = {'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'concurso_uuid' in serializer.errors

    def test_serializer_invalido_sem_processo_uuid(self) -> None:
        """Testa serializer inválido sem processo_uuid."""
        concurso_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'processo_uuid' in serializer.errors

    def test_serializer_invalido_sem_escolhas(self) -> None:
        """Testa serializer inválido sem escolhas."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid)}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'escolhas' in serializer.errors

    def test_serializer_invalido_escolhas_vazia(self) -> None:
        """Testa serializer inválido com lista de escolhas vazia."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': []}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'escolhas' in serializer.errors

    def test_serializer_invalido_escolha_sem_cpf(self) -> None:
        """Testa serializer inválido com escolha sem CPF."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'codigo_cargo': '123', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'escolhas' in serializer.errors or any(('cpf' in str(err).lower() for err in serializer.errors.values()))

    def test_serializer_invalido_escolha_sem_codigo_cargo(self) -> None:
        """Testa serializer inválido com escolha sem codigo_cargo."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'escolhas' in serializer.errors or any(('codigo_cargo' in str(err).lower() for err in serializer.errors.values()))

    def test_serializer_invalido_escolha_sem_situacao(self) -> None:
        """Testa serializer inválido com escolha sem situacao."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'escolhas' in serializer.errors or any(('situacao' in str(err).lower() for err in serializer.errors.values()))

    def test_validate_escolhas_cpf_obrigatorio(self) -> None:
        """Testa validação customizada que CPF é obrigatório."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '', 'codigo_cargo': '123', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_escolhas_codigo_cargo_obrigatorio(self) -> None:
        """Testa validação customizada que codigo_cargo é obrigatório."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '', 'situacao': 'ESCOLHA'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_escolhas_situacao_obrigatoria(self) -> None:
        """Testa validação customizada que situacao é obrigatória."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123', 'situacao': ''}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_serializer_multiplas_escolhas(self) -> None:
        """Testa serializer com múltiplas escolhas válidas."""
        concurso_uuid = uuid.uuid4()
        processo_uuid = uuid.uuid4()
        data = {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'escolhas': [{'cpf': '12345678901', 'codigo_cargo': '123', 'codigo_eol': '456789', 'tipo_vaga': 'P', 'situacao': 'ESCOLHA'}, {'cpf': '98765432100', 'codigo_cargo': '456', 'situacao': 'NAO-ESCOLHA'}, {'cpf': '11122233344', 'codigo_cargo': '789', 'codigo_eol': '123456', 'tipo_vaga': 'D', 'situacao': 'RECONVOCACAO'}]}
        serializer = EscolhasProdamImportacaoSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.validated_data['escolhas']) == 3
