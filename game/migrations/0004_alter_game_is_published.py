# Generated by Django 4.2.13 on 2024-08-22 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_alter_game_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='is_published',
            field=models.BooleanField(choices=[(False, 'Черновик'), (True, 'Опубликовано')], default=0, verbose_name='Статус'),
        ),
    ]
