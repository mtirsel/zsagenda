# Generated by Django 2.1.5 on 2019-01-17 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regform', '0006_auto_20190116_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationanswer',
            name='identifier',
            field=models.CharField(blank=True, default=None, max_length=10, null=True, unique=True, verbose_name='přidělený identifikátor'),
        ),
        migrations.AlterField(
            model_name='registrationanswer',
            name='reg_date',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to='regform.RegistrationDate', verbose_name='Termín pro registraci'),
        ),
    ]
