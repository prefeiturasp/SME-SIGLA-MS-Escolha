"""Testes da migração de PK UUID para id inteiro (0021 a 0023)."""

from __future__ import annotations

import importlib
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.db.models import Max

from escola.models import Dre

ANTES = ("escolhas", "0020_escolha_processo_uuid")
CARGA = ("escolhas", "0022_popula_novo_id")
DEPOIS = ("escolhas", "0023_troca_pk_uuid_por_id")
MODELOS = [
    "Dre",
    "Escola",
    "VagasEscolasLote",
    "VagasEscolas",
    "Escolha",
    "HistoricoEscolha",
    "Parametrizacao",
]
MODELOS_DA_CADEIA = [nome for nome in MODELOS if nome != "Parametrizacao"]
FKS = [
    ("Escola", "dre", "Dre"),
    ("VagasEscolas", "lote", "VagasEscolasLote"),
    ("VagasEscolas", "escola", "Escola"),
    ("Escolha", "vaga_escola", "VagasEscolas"),
    ("HistoricoEscolha", "escolha", "Escolha"),
]
DEPENDENCIAS_AUDITLOG = [
    ("contenttypes", "0002_remove_content_type_name"),
    ("auditlog", "0017_add_actor_email"),
]
INSTANTE_BASE = datetime(2026, 1, 1, tzinfo=UTC)

Migrar = Callable[[tuple[str, str]], StateApps]


@pytest.fixture
def migrar(transactional_db: Any) -> Iterator[Migrar]:
    """Migra o banco de testes até um nó e devolve os modelos históricos.

    Os modelos de ``contenttypes`` e ``auditlog`` vêm junto no estado
    devolvido, para que os testes criem ``LogEntry`` antes da carga.

    Yields:
        Função que recebe o nó alvo e devolve o ``StateApps`` dele.
    """

    def _migrar(alvo: tuple[str, str]) -> StateApps:
        MigrationExecutor(connection).migrate([alvo])
        loader = MigrationExecutor(connection).loader
        return loader.project_state([alvo, *DEPENDENCIAS_AUDITLOG]).apps

    yield _migrar

    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())


def _criar(modelo: Any, instante: datetime, **campos: Any) -> Any:
    """Cria o registro e fixa ``criado_em`` (``auto_now_add``) em ``instante``.

    Args:
        modelo: Modelo histórico.
        instante: Valor desejado para ``criado_em``.
        **campos: Campos do registro.

    Returns:
        O registro criado, com ``criado_em`` já ajustado.
    """
    registro = modelo.objects.create(**campos)
    modelo.objects.filter(pk=registro.pk).update(criado_em=instante)
    registro.criado_em = instante
    return registro


def _criar_dre(apps: StateApps, instante: datetime, **campos: Any) -> Any:
    """Cria uma DRE histórica."""
    dados = {"codigo": "01", "nome": "DRE", "sigla": "DRE"} | campos
    return _criar(apps.get_model("escolhas", "Dre"), instante, **dados)


def _criar_cadeia(apps: StateApps, instante: datetime) -> dict[str, Any]:
    """Cria Dre, Escola, lote, vaga, escolha e histórico encadeados.

    Args:
        apps: Modelos históricos.
        instante: ``criado_em`` de todos os registros da cadeia.

    Returns:
        Os registros criados, indexados pelo nome do modelo em minúsculas.
    """
    dre = _criar_dre(apps, instante)
    escola = _criar(
        apps.get_model("escolhas", "Escola"),
        instante,
        dre=dre,
        codigo_eol="000001",
    )
    lote = _criar(
        apps.get_model("escolhas", "VagasEscolasLote"),
        instante,
        processo_uuid=uuid.uuid4(),
    )
    vaga = _criar(
        apps.get_model("escolhas", "VagasEscolas"),
        instante,
        lote=lote,
        escola=escola,
        data_fechamento_modulo=instante.date(),
        cargo_codigo=1,
    )
    escolha = _criar(
        apps.get_model("escolhas", "Escolha"), instante, vaga_escola=vaga
    )
    historico = _criar(
        apps.get_model("escolhas", "HistoricoEscolha"),
        instante,
        escolha=escolha,
        situacao_nova="ESCOLHA",
    )
    return {
        "dre": dre,
        "escola": escola,
        "vagasescolaslote": lote,
        "vagasescolas": vaga,
        "escolha": escolha,
        "historicoescolha": historico,
    }


def _criar_log_entry(apps: StateApps, nome_modelo: str, object_pk: str) -> Any:
    """Cria um ``LogEntry`` no formato antigo (``object_id`` nulo).

    Args:
        apps: Modelos históricos, com ``contenttypes`` e ``auditlog``.
        nome_modelo: Nome do modelo do ContentType, em minúsculas.
        object_pk: Valor gravado em ``object_pk``.

    Returns:
        O ``LogEntry`` criado.
    """
    tipo, _ = apps.get_model(
        "contenttypes", "ContentType"
    ).objects.get_or_create(app_label="escolhas", model=nome_modelo)
    return apps.get_model("auditlog", "LogEntry").objects.create(
        content_type=tipo,
        object_pk=object_pk,
        object_id=None,
        object_repr="registro",
        action=0,
    )


@pytest.mark.django_db(transaction=True)
def test_novo_id_segue_ordem_de_criacao(migrar: Migrar) -> None:
    """Numera por ``criado_em`` e desempata por ``uuid``."""
    antes = migrar(ANTES)
    t0 = INSTANTE_BASE
    t1 = t0 + timedelta(hours=1)
    _criar_dre(antes, t1, uuid=uuid.UUID(int=2))
    _criar_dre(antes, t1, uuid=uuid.UUID(int=1))
    _criar_dre(antes, t0, uuid=uuid.UUID(int=3))

    carga = migrar(CARGA)

    Dre = carga.get_model("escolhas", "Dre")
    novo_id_por_uuid = dict(Dre.objects.values_list("uuid", "novo_id"))
    assert novo_id_por_uuid == {
        uuid.UUID(int=3): 1,
        uuid.UUID(int=1): 2,
        uuid.UUID(int=2): 3,
    }


@pytest.mark.django_db(transaction=True)
def test_fk_novo_recebe_novo_id_do_pai(migrar: Migrar) -> None:
    """Cada ``<fk>_novo`` recebe o ``novo_id`` do registro pai."""
    antes = migrar(ANTES)
    _criar_dre(antes, INSTANTE_BASE)
    cadeias = [
        _criar_cadeia(antes, INSTANTE_BASE + timedelta(hours=horas))
        for horas in (1, 2)
    ]

    carga = migrar(CARGA)

    def recarregar(nome_modelo: str, registro: Any) -> Any:
        return carga.get_model("escolhas", nome_modelo).objects.get(
            pk=registro.pk
        )

    for cadeia in cadeias:
        pais = {
            nome: recarregar(nome, registro)
            for nome, registro in cadeia.items()
        }
        assert pais["escola"].dre_novo == pais["dre"].novo_id
        assert (
            pais["vagasescolas"].lote_novo == pais["vagasescolaslote"].novo_id
        )
        assert pais["vagasescolas"].escola_novo == pais["escola"].novo_id
        assert pais["escolha"].vaga_escola_novo == pais["vagasescolas"].novo_id
        assert pais["historicoescolha"].escolha_novo == pais["escolha"].novo_id
    segunda = {
        nome: recarregar(nome, registro)
        for nome, registro in cadeias[1].items()
    }
    assert segunda["dre"].novo_id == 3
    assert segunda["escola"].dre_novo == 3
    assert segunda["vagasescolas"].escola_novo == 2


@pytest.mark.django_db(transaction=True)
def test_fk_nula_continua_nula(migrar: Migrar) -> None:
    """Escolha sem vaga e vaga sem lote ficam com a FK provisória nula."""
    antes = migrar(ANTES)
    dre = _criar_dre(antes, INSTANTE_BASE)
    escola = _criar(
        antes.get_model("escolhas", "Escola"),
        INSTANTE_BASE,
        dre=dre,
        codigo_eol="000001",
    )
    vaga = _criar(
        antes.get_model("escolhas", "VagasEscolas"),
        INSTANTE_BASE,
        lote=None,
        escola=escola,
        data_fechamento_modulo=INSTANTE_BASE.date(),
        cargo_codigo=1,
    )
    escolha = _criar(
        antes.get_model("escolhas", "Escolha"), INSTANTE_BASE, vaga_escola=None
    )

    carga = migrar(CARGA)

    vaga_carga = carga.get_model("escolhas", "VagasEscolas").objects.get(
        pk=vaga.pk
    )
    escolha_carga = carga.get_model("escolhas", "Escolha").objects.get(
        pk=escolha.pk
    )
    assert vaga_carga.lote_novo is None
    assert vaga_carga.escola_novo is not None
    assert escolha_carga.vaga_escola_novo is None


@pytest.mark.django_db(transaction=True)
def test_logentry_aponta_para_novo_id(migrar: Migrar) -> None:
    """O ``LogEntry`` do registro passa a apontar para o ``novo_id``."""
    antes = migrar(ANTES)
    _criar(antes.get_model("escolhas", "Escolha"), INSTANTE_BASE)
    escolha = _criar(
        antes.get_model("escolhas", "Escolha"),
        INSTANTE_BASE + timedelta(hours=1),
    )
    entrada = _criar_log_entry(antes, "escolha", str(escolha.uuid))

    carga = migrar(CARGA)

    novo_id = (
        carga.get_model("escolhas", "Escolha")
        .objects.get(pk=escolha.pk)
        .novo_id
    )
    entrada_carga = carga.get_model("auditlog", "LogEntry").objects.get(
        pk=entrada.pk
    )
    assert novo_id == 2
    assert entrada_carga.object_id == novo_id
    assert entrada_carga.object_pk == str(novo_id)


@pytest.mark.django_db(transaction=True)
def test_logentry_de_objeto_apagado_fica_intocado(migrar: Migrar) -> None:
    """``LogEntry`` sem registro correspondente não é alterado."""
    antes = migrar(ANTES)
    _criar(antes.get_model("escolhas", "Escolha"), INSTANTE_BASE)
    uuid_apagado = str(uuid.uuid4())
    entrada = _criar_log_entry(antes, "escolha", uuid_apagado)

    carga = migrar(CARGA)

    entrada_carga = carga.get_model("auditlog", "LogEntry").objects.get(
        pk=entrada.pk
    )
    assert entrada_carga.object_id is None
    assert entrada_carga.object_pk == uuid_apagado


@pytest.mark.django_db(transaction=True)
def test_logentry_com_object_pk_invalido_fica_intocado(migrar: Migrar) -> None:
    """``object_pk`` que não é UUID é ignorado, sem interromper a carga."""
    antes = migrar(ANTES)
    escolha = _criar(antes.get_model("escolhas", "Escolha"), INSTANTE_BASE)
    invalida = _criar_log_entry(antes, "escolha", "nao-e-uuid")
    valida = _criar_log_entry(antes, "escolha", str(escolha.uuid))

    carga = migrar(CARGA)

    LogEntry = carga.get_model("auditlog", "LogEntry")
    invalida_carga = LogEntry.objects.get(pk=invalida.pk)
    valida_carga = LogEntry.objects.get(pk=valida.pk)
    assert invalida_carga.object_id is None
    assert invalida_carga.object_pk == "nao-e-uuid"
    assert valida_carga.object_id == 1


@pytest.mark.django_db(transaction=True)
def test_volta_da_carga_restaura_logentry(migrar: Migrar) -> None:
    """Reverter a 0022 devolve ``object_pk`` em UUID e ``object_id`` nulo."""
    antes = migrar(ANTES)
    _criar(antes.get_model("escolhas", "Escolha"), INSTANTE_BASE)
    escolha = _criar(
        antes.get_model("escolhas", "Escolha"),
        INSTANTE_BASE + timedelta(hours=1),
    )
    entrada = _criar_log_entry(antes, "escolha", str(escolha.uuid))
    uuid_apagado = str(uuid.uuid4())
    entrada_apagada = _criar_log_entry(antes, "escolha", uuid_apagado)

    carga = migrar(CARGA)
    LogEntry = carga.get_model("auditlog", "LogEntry")
    remapeada = LogEntry.objects.get(pk=entrada.pk)
    assert (remapeada.object_pk, remapeada.object_id) == ("2", 2)

    restaurado = migrar(ANTES).get_model("auditlog", "LogEntry")

    entrada_restaurada = restaurado.objects.get(pk=entrada.pk)
    assert entrada_restaurada.object_pk == str(escolha.uuid)
    assert entrada_restaurada.object_id is None
    apagada_restaurada = restaurado.objects.get(pk=entrada_apagada.pk)
    assert apagada_restaurada.object_pk == uuid_apagado
    assert apagada_restaurada.object_id is None


@pytest.mark.django_db(transaction=True)
def test_carga_e_volta_em_varios_lotes(
    migrar: Migrar, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Numeração e remapeamento do log valem com vários lotes de gravação."""
    migracao = importlib.import_module(
        "escolhas.migrations.0022_popula_novo_id"
    )
    monkeypatch.setattr(migracao, "TAMANHO_LOTE", 2)
    antes = migrar(ANTES)
    escolhas = [
        _criar(
            antes.get_model("escolhas", "Escolha"),
            INSTANTE_BASE + timedelta(hours=horas),
        )
        for horas in range(5)
    ]
    entradas = [
        _criar_log_entry(antes, "escolha", str(escolha.uuid))
        for escolha in escolhas
    ]

    carga = migrar(CARGA)

    Escolha = carga.get_model("escolhas", "Escolha")
    LogEntry = carga.get_model("auditlog", "LogEntry")
    assert [
        Escolha.objects.get(pk=escolha.pk).novo_id for escolha in escolhas
    ] == [1, 2, 3, 4, 5]
    assert [
        (e.object_pk, e.object_id)
        for e in (LogEntry.objects.get(pk=entrada.pk) for entrada in entradas)
    ] == [(str(numero), numero) for numero in range(1, 6)]

    restaurado = migrar(ANTES).get_model("auditlog", "LogEntry")

    assert [
        (e.object_pk, e.object_id)
        for e in (
            restaurado.objects.get(pk=entrada.pk) for entrada in entradas
        )
    ] == [(str(escolha.uuid), None) for escolha in escolhas]


def _tabela(apps: StateApps, nome_modelo: str) -> str:
    """Devolve o ``db_table`` do modelo histórico."""
    return str(apps.get_model("escolhas", nome_modelo)._meta.db_table)


@pytest.mark.django_db(transaction=True)
def test_id_vira_pk_com_a_numeracao_da_carga(migrar: Migrar) -> None:
    """``id`` vira a PK com a numeração da carga e o ``uuid`` é mantido."""
    antes = migrar(ANTES)
    t0 = INSTANTE_BASE
    t1 = t0 + timedelta(hours=1)
    _criar_dre(antes, t1, uuid=uuid.UUID(int=2))
    _criar_dre(antes, t1, uuid=uuid.UUID(int=1))
    _criar_dre(antes, t0, uuid=uuid.UUID(int=3))
    parametrizacao = _criar(
        antes.get_model("escolhas", "Parametrizacao"), t0, tipo_ue="EMEF"
    )

    depois = migrar(DEPOIS)

    dres = depois.get_model("escolhas", "Dre").objects
    assert dict(dres.values_list("uuid", "pk")) == {
        uuid.UUID(int=3): 1,
        uuid.UUID(int=1): 2,
        uuid.UUID(int=2): 3,
    }
    parametrizacoes = depois.get_model("escolhas", "Parametrizacao").objects
    assert list(parametrizacoes.values_list("uuid", "pk")) == [
        (parametrizacao.uuid, 1)
    ]
    with connection.cursor() as cursor:
        for nome in MODELOS:
            assert connection.introspection.get_primary_key_columns(
                cursor, _tabela(depois, nome)
            ) == ["id"], nome


@pytest.mark.django_db(transaction=True)
def test_fks_apontam_para_id(migrar: Migrar) -> None:
    """Cada FK aponta para o ``id`` do mesmo pai; as nulas seguem nulas."""
    antes = migrar(ANTES)
    _criar_dre(antes, INSTANTE_BASE)
    cadeias = [
        _criar_cadeia(antes, INSTANTE_BASE + timedelta(hours=horas))
        for horas in (1, 2)
    ]
    t3 = INSTANTE_BASE + timedelta(hours=3)
    vaga_sem_lote = _criar(
        antes.get_model("escolhas", "VagasEscolas"),
        t3,
        lote=None,
        escola=cadeias[1]["escola"],
        data_fechamento_modulo=t3.date(),
        cargo_codigo=1,
    )
    escolha_sem_vaga = _criar(
        antes.get_model("escolhas", "Escolha"), t3, vaga_escola=None
    )

    depois = migrar(DEPOIS)

    def recarregar(nome_modelo: str, registro: Any) -> Any:
        return depois.get_model("escolhas", nome_modelo).objects.get(
            uuid=registro.uuid
        )

    for posicao, cadeia in enumerate(cadeias, start=1):
        registros = {
            nome: recarregar(nome, cadeia[nome.lower()])
            for nome in MODELOS_DA_CADEIA
        }
        assert {nome: r.id for nome, r in registros.items()} == {
            "Dre": posicao + 1,
            "Escola": posicao,
            "VagasEscolasLote": posicao,
            "VagasEscolas": posicao,
            "Escolha": posicao,
            "HistoricoEscolha": posicao,
        }
        for filho, campo, pai in FKS:
            registro_filho = registros[filho]
            assert getattr(registro_filho, f"{campo}_id") == registros[pai].id
            assert (
                getattr(registro_filho, campo).uuid == cadeia[pai.lower()].uuid
            )
    vaga = recarregar("VagasEscolas", vaga_sem_lote)
    escolha = recarregar("Escolha", escolha_sem_vaga)
    assert (vaga.id, vaga.lote_id, vaga.escola_id) == (3, None, 2)
    assert (escolha.id, escolha.vaga_escola_id) == (3, None)
    with connection.cursor() as cursor:
        for filho, campo, pai in FKS:
            relacoes = connection.introspection.get_relations(
                cursor, _tabela(depois, filho)
            )
            assert relacoes[f"{campo}_id"] == ("id", _tabela(depois, pai))


@pytest.mark.django_db(transaction=True)
def test_proximo_insert_continua_a_sequencia(migrar: Migrar) -> None:
    """O primeiro INSERT depois da 0023 recebe ``max(id) + 1``."""
    antes = migrar(ANTES)
    _criar_dre(antes, INSTANTE_BASE)
    for horas in (1, 2):
        _criar_cadeia(antes, INSTANTE_BASE + timedelta(hours=horas))
    for tipo_ue in ("EMEF", "EMEI"):
        _criar(
            antes.get_model("escolhas", "Parametrizacao"),
            INSTANTE_BASE,
            tipo_ue=tipo_ue,
        )

    depois = migrar(DEPOIS)

    maximos = {
        nome: depois.get_model("escolhas", nome).objects.aggregate(
            maximo=Max("id")
        )["maximo"]
        for nome in MODELOS
    }
    assert maximos == {
        "Dre": 3,
        "Escola": 2,
        "VagasEscolasLote": 2,
        "VagasEscolas": 2,
        "Escolha": 2,
        "HistoricoEscolha": 2,
        "Parametrizacao": 2,
    }
    instante = INSTANTE_BASE + timedelta(hours=3)
    nova_cadeia = _criar_cadeia(depois, instante)
    nova_parametrizacao = _criar(
        depois.get_model("escolhas", "Parametrizacao"),
        instante,
        tipo_ue="CEU",
    )
    novos_ids = {
        nome: nova_cadeia[nome.lower()].id for nome in MODELOS_DA_CADEIA
    } | {"Parametrizacao": nova_parametrizacao.id}
    assert novos_ids == {nome: maximo + 1 for nome, maximo in maximos.items()}


@pytest.mark.django_db(transaction=True)
def test_uuid_continua_unico(migrar: Migrar) -> None:
    """O ``uuid`` deixa de ser PK, mas segue único no banco."""
    antes = migrar(ANTES)
    dre = _criar_dre(antes, INSTANTE_BASE)

    depois = migrar(DEPOIS)

    with pytest.raises(IntegrityError), transaction.atomic():
        _criar_dre(depois, INSTANTE_BASE, uuid=dre.uuid)
    with connection.cursor() as cursor:
        for nome in MODELOS:
            restricoes = connection.introspection.get_constraints(
                cursor, _tabela(depois, nome)
            )
            assert any(
                restricao["unique"]
                and not restricao["primary_key"]
                and restricao["columns"] == ["uuid"]
                for restricao in restricoes.values()
            ), nome


@pytest.mark.django_db
def test_modelos_e_migrations_em_sincronia() -> None:
    """``makemigrations --check`` não encontra mudança pendente."""
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


@pytest.mark.django_db
def test_base_model_usa_id_inteiro() -> None:
    """Os modelos atuais têm ``id`` inteiro como PK e ``uuid`` preenchido."""
    dre = Dre.objects.create(codigo="01", nome="DRE", sigla="DRE")

    assert Dre._meta.pk is not None
    assert Dre._meta.pk.name == "id"
    assert isinstance(dre.pk, int)
    assert isinstance(dre.uuid, uuid.UUID)
