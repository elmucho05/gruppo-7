# Generated by Django 4.2 on 2023-05-25 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_remove_chessroom_player_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chessroom',
            name='room_mode',
            field=models.IntegerField(default=0),
        ),
    ]
