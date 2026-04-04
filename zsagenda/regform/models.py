from django.db import models


class RegistrationDate(models.Model):
    date = models.DateTimeField(verbose_name='Termín')

    class Meta:
        ordering = ['date']
        verbose_name = 'Termíny pro registraci'
        verbose_name_plural = 'Termíny pro registraci'

    def __str__(self):
        return self.date.strftime('%d.%m.%Y %H:%M')

    def is_available(self):
        try:
            self.registrationanswer
            return False
        except RegistrationAnswer.DoesNotExist:
            return True


class RegistrationAnswer(models.Model):
    reg_date = models.OneToOneField(
        RegistrationDate,
        verbose_name='Termín pro registraci',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name='e-mail',
        help_text='Na tuto e-mailovou adresu obdržíte potvrzení o termínu zápisu.'
    )
    child_name = models.CharField(
        verbose_name='jméno a příjmení dítěte',
        max_length=100
    )
    parent_name = models.CharField(
        verbose_name='jméno a příjmení zákonného zástupce',
        max_length=100
    )
    child_birth_date = models.DateField(
        verbose_name='datum narození',
        help_text='Ve formátu D.M.RRRR, např. 15.4.2013'
    )
    phone = models.CharField(
        verbose_name='telefon',
        max_length=255,
    )
    address = models.CharField(
        verbose_name='adresa trvalého bydliště',
        max_length=255
    )
    identifier = models.CharField(
        verbose_name='přidělený identifikátor',
        max_length=10,
        blank=True,
        default=None,
        null=True,
        unique=True,
    )
    note = models.TextField(
        verbose_name='interní poznámka',
        blank=True,
        default=''
    )
    possible_postponement = models.PositiveSmallIntegerField(
        verbose_name='zvažujete odklad školní docházky?',
        choices=(
            (0, 'neznámo'),
            (10, 'ano'),
            (20, 'ne'),
        ),
        default=0,
    )
    email_sent = models.BooleanField(
        verbose_name='e-mail byl úspěšně odeslán',
        default=False,
        blank=True,
    )
    substitute = models.BooleanField(
        verbose_name='náhradník',
        default=False,
    )
    created = models.DateTimeField(
        verbose_name='Vytvořeno',
        auto_now_add=True
    )
    modified = models.DateTimeField(
        verbose_name='Změněno',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Odpovědi z registrace'
        verbose_name_plural = 'Odpovědi z registrace'


class SubstituteContact(models.Model):
    name = models.CharField(
        verbose_name='jméno',
        max_length=100
    )
    email = models.EmailField(
        verbose_name='e-mail',
    )
    phone = models.CharField(
        verbose_name='telefon',
        max_length=255,
    )
    created = models.DateTimeField(
        verbose_name='Vytvořeno',
        auto_now_add=True
    )
    modified = models.DateTimeField(
        verbose_name='Změněno',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Evidence náhradníků'
        verbose_name_plural = 'Evidence náhradníků'
