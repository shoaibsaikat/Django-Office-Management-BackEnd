# Generated by Django 3.1.2 on 2022-01-25 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0005_remove_asset_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
