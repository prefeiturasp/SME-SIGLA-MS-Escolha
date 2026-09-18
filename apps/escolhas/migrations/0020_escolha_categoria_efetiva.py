# Generated manually for extracao-dados breakdown by categoria

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escolhas", "0019_vagasescolaslote_concurso_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="escolha",
            name="categoria_efetiva",
            field=models.CharField(
                blank=True,
                choices=[
                    ("GERAL", "Geral"),
                    ("PCD", "PCD"),
                    ("NNA", "NNA"),
                ],
                db_index=True,
                max_length=10,
                null=True,
                verbose_name="Categoria efetiva",
            ),
        ),
    ]
