# Generated by Django 4.2 on 2023-05-31 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_rename_is_qualified_chesstournamentlobby_player_is_qualified_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chesstournament',
            name='tournament_status',
            field=models.CharField(choices=[('WAITING_FOR_PLAYER', 'WAITING_FOR_PLAYER'), ('READY_TO_DRAW', 'READY_TO_DRAW'), ('PLAYERS_IN_GAME', 'PLAYERS_IN_GAME'), ('TOURNAMENT_CLOSED', 'TOURNAMENT_CLOSED')], default='WAITING_FOR_PLAYER', max_length=20),
        ),
    ]
