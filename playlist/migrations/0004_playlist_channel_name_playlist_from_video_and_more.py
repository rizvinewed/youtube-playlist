# Generated by Django 4.2.2 on 2024-06-30 22:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("playlist", "0003_playlist_ip_address_playlist_metadata"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="channel_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="playlist",
            name="from_video",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="playlist",
            name="to_video",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
