# Generated by Django 2.1.5 on 2019-01-17 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regform', '0007_auto_20190117_2324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registrationanswer',
            old_name='child_brith_date',
            new_name='child_birth_date',
        ),
    ]