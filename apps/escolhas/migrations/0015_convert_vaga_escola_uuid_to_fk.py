# Generated migration to convert vaga_escola_uuid to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


def migrate_uuid_to_fk(apps, schema_editor):
    """
    Migra os dados de vaga_escola_uuid para vaga_escola (ForeignKey).
    """
    Escolha = apps.get_model('escolhas', 'Escolha')
    VagasEscolas = apps.get_model('escolhas', 'VagasEscolas')
    
    # Iterar sobre todas as escolhas que têm vaga_escola_uuid
    for escolha in Escolha.objects.filter(vaga_escola_uuid__isnull=False):
        try:
            # Buscar a VagasEscolas pelo UUID
            vaga_escola = VagasEscolas.objects.get(uuid=escolha.vaga_escola_uuid)
            # Atribuir a ForeignKey
            escolha.vaga_escola = vaga_escola
            escolha.save(update_fields=['vaga_escola'])
        except VagasEscolas.DoesNotExist:
            # Se não encontrar a vaga, deixa como None (SET_NULL)
            escolha.vaga_escola = None
            escolha.save(update_fields=['vaga_escola'])


def reverse_migrate(apps, schema_editor):
    """
    Reverte a migração: converte ForeignKey de volta para UUID.
    """
    Escolha = apps.get_model('escolhas', 'Escolha')
    
    # Iterar sobre todas as escolhas que têm vaga_escola
    for escolha in Escolha.objects.filter(vaga_escola__isnull=False):
        # Atribuir o UUID da ForeignKey ao campo UUID
        escolha.vaga_escola_uuid = escolha.vaga_escola.uuid
        escolha.save(update_fields=['vaga_escola_uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('escolhas', '0014_add_vagas_restantes'),
    ]

    operations = [
        # 1. Adicionar novo campo ForeignKey (temporariamente null=True para permitir migração)
        migrations.AddField(
            model_name='escolha',
            name='vaga_escola',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='escolhas',
                to='escolhas.vagasescolas',
                verbose_name='Vaga da Escola'
            ),
        ),
        # 2. Migrar os dados de UUID para ForeignKey
        migrations.RunPython(migrate_uuid_to_fk, reverse_migrate),
        # 3. Remover o campo antigo UUID
        migrations.RemoveField(
            model_name='escolha',
            name='vaga_escola_uuid',
        ),
    ]
