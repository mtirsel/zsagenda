# Generated by Django 2.1.15 on 2023-01-31 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regform', '0013_registrationanswer_substitute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationanswer',
            name='reg_date',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='regform.RegistrationDate', verbose_name='Termín pro registraci'),
        ),
    ]
