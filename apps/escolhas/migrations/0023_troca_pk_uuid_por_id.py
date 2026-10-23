"""Troca a PK UUID pelo ``id`` inteiro carregado na 0022."""

import uuid

import django.db.models.deletion
from django.core.management.color import no_style
from django.db import migrations, models

MODELOS = [
    "Dre",
    "Escola",
    "VagasEscolasLote",
    "VagasEscolas",
    "Escolha",
    "HistoricoEscolha",
    "Parametrizacao",
]

# (filho, campo da FK, pai); a coluna provisória é ``<campo>_novo``.
FKS = [
    ("Escola", "dre", "Dre"),
    ("VagasEscolas", "lote", "VagasEscolasLote"),
    ("VagasEscolas", "escola", "Escola"),
    ("Escolha", "vaga_escola", "VagasEscolas"),
    ("HistoricoEscolha", "escolha", "Escolha"),
]


def reiniciar_sequencias(apps, schema_editor):
    """Faz a sequência de cada ``id`` continuar depois do maior valor.

    No PostgreSQL a coluna vira identity começando em 1, e sem este passo
    o primeiro INSERT colidiria com os ids da carga. No SQLite a lista de
    comandos vem vazia.

    Args:
        apps: Registro de modelos históricos da migration.
        schema_editor: Editor de esquema da conexão em uso.
    """
    conexao = schema_editor.connection
    modelos = [apps.get_model("escolhas", nome) for nome in MODELOS]
    with conexao.cursor() as cursor:
        for sql in conexao.ops.sequence_reset_sql(no_style(), modelos):
            cursor.execute(sql)


class Migration(migrations.Migration):
    """Promove ``novo_id`` a PK ``id`` e refaz as FKs apontando para ele.

    As FKs antigas saem primeiro, para o banco deixar remover a PK do
    ``uuid``. O nome provisório ``novo_id`` evita colidir com o ``id`` que
    o Django cria no estado intermediário, quando o modelo fica sem PK.
    ``novo_id`` vira NOT NULL antes de virar PK: na volta, o PostgreSQL
    só aceita o DROP NOT NULL depois que a PK sai.
    """

    dependencies = [
        ("escolhas", "0022_popula_novo_id"),
    ]

    operations = [
        *[
            migrations.RemoveField(model_name=filho.lower(), name=campo)
            for filho, campo, _ in FKS
        ],
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="uuid",
                field=models.UUIDField(
                    default=uuid.uuid4, editable=False, unique=True
                ),
            )
            for nome in MODELOS
        ],
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="novo_id",
                field=models.BigIntegerField(editable=False),
            )
            for nome in MODELOS
        ],
        *[
            migrations.AlterField(
                model_name=nome.lower(),
                name="novo_id",
                field=models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID",
                ),
            )
            for nome in MODELOS
        ],
        *[
            migrations.RenameField(
                model_name=nome.lower(), old_name="novo_id", new_name="id"
            )
            for nome in MODELOS
        ],
        migrations.RenameField(
            model_name="escola", old_name="dre_novo", new_name="dre"
        ),
        migrations.AlterField(
            model_name="escola",
            name="dre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="escolhas.dre",
                verbose_name="DRE",
            ),
        ),
        migrations.RenameField(
            model_name="vagasescolas", old_name="lote_novo", new_name="lote"
        ),
        migrations.AlterField(
            model_name="vagasescolas",
            name="lote",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vagas",
                to="escolhas.vagasescolaslote",
                verbose_name="Lote do Processo",
            ),
        ),
        migrations.RenameField(
            model_name="vagasescolas",
            old_name="escola_novo",
            new_name="escola",
        ),
        migrations.AlterField(
            model_name="vagasescolas",
            name="escola",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vagas_escolas",
                to="escolhas.escola",
                verbose_name="Escola",
            ),
        ),
        migrations.RenameField(
            model_name="escolha",
            old_name="vaga_escola_novo",
            new_name="vaga_escola",
        ),
        migrations.AlterField(
            model_name="escolha",
            name="vaga_escola",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="escolhas",
                to="escolhas.vagasescolas",
                verbose_name="Vaga da Escola",
            ),
        ),
        migrations.RenameField(
            model_name="historicoescolha",
            old_name="escolha_novo",
            new_name="escolha",
        ),
        migrations.AlterField(
            model_name="historicoescolha",
            name="escolha",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="historico",
                to="escolhas.escolha",
                verbose_name="Escolha",
            ),
        ),
        migrations.RunPython(reiniciar_sequencias, migrations.RunPython.noop),
    ]
