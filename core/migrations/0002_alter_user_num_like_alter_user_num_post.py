# Generated by Django 4.1.7 on 2024-04-02 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='num_Like',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='num_Post',
            field=models.IntegerField(null=True),
        ),
    ]
