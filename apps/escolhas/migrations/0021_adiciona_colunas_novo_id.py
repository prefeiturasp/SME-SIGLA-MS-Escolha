"""Adiciona as colunas provisórias da troca de PK UUID por id inteiro."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Cria ``novo_id`` nos 7 modelos e as FKs provisórias nos filhos."""

    dependencies = [
        ("escolhas", "0020_escolha_processo_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="dre",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="escola",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="vagasescolaslote",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="vagasescolas",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="escolha",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="historicoescolha",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="parametrizacao",
            name="novo_id",
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="escola",
            name="dre_novo",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="vagasescolas",
            name="lote_novo",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="vagasescolas",
            name="escola_novo",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="escolha",
            name="vaga_escola_novo",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="historicoescolha",
            name="escolha_novo",
            field=models.BigIntegerField(null=True),
        ),
    ]
