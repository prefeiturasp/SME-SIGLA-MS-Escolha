# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escolhas", "0019_vagasescolaslote_concurso_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="escolha",
            name="processo_uuid",
            field=models.UUIDField(
                blank=True, null=True, verbose_name="UUID do Processo"
            ),
        ),
    ]
