# Generated by Django 5.0.6 on 2024-10-03 18:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chooseclass',
            name='ccgrade',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='student',
            name='sconcern',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(500)]),
        ),
        migrations.AlterField(
            model_name='student',
            name='sfans',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(500)]),
        ),
        migrations.AlterField(
            model_name='student',
            name='sfavor',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(500)]),
        ),
    ]
