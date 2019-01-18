
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regform', '0008_auto_20190117_2348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registrationanswer',
            old_name='contact',
            new_name='phone',
        ),
        migrations.AlterField(
            model_name='registrationanswer',
            name='phone',
            field=models.CharField(max_length=255, verbose_name='telefon'),
        ),
    ]
