# Generated by Django 2.1.5 on 2019-01-18 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regform', '0009_auto_20190118_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubstituteContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='jméno')),
                ('email', models.EmailField(max_length=254, verbose_name='e-mail')),
                ('phone', models.CharField(max_length=255, verbose_name='telefon')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Vytvořeno')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Změněno')),
            ],
        ),
    ]
