# Generated by Django 4.2 on 2023-05-25 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_remove_chesstournamentlobby_num_total_players_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chesstournament',
            name='num_total_players',
        ),
        migrations.RemoveField(
            model_name='chesstrackplayers',
            name='type',
        ),
        migrations.AddField(
            model_name='chesstournamentlobby',
            name='is_qualified',
            field=models.BooleanField(default=True),
        ),
    ]
