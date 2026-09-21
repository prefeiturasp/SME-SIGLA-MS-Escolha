# Generated manually: categoria efetiva passa a vir do MS-Candidatos na extração

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("escolhas", "0020_escolha_categoria_efetiva"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="escolha",
            name="categoria_efetiva",
        ),
    ]
