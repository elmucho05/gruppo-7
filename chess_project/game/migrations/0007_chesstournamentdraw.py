# Generated by Django 4.2 on 2023-05-31 08:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0006_remove_chesstournament_num_total_players_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChessTournamentDraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player1', to=settings.AUTH_USER_MODEL)),
                ('player2', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player2', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.chesstournament')),
            ],
            options={
                'unique_together': {('player1', 'player2')},
            },
        ),
    ]
