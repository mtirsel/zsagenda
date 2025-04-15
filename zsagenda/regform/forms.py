
import datetime

from django import forms
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.utils.safestring import mark_safe

from regform.models import RegistrationAnswer
from regform.models import RegistrationDate
from regform.models import SubstituteContact


class RegistrationFailedException(Exception):
    pass


class BaseRegistrationForm(forms.ModelForm):
    class Meta:
        model = RegistrationAnswer
        fields = []
        widgets = {
            'possible_postponement': forms.widgets.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove default choice "neznámo"
        self.fields['possible_postponement'].choices = self.fields['possible_postponement'].choices[1:]


class RegistrationAnswerForm(BaseRegistrationForm):
    ERR_MSG_UNAVAILABLE_REG_DATE = 'Tento termín již není k dispozici, zvolte prosím jiný.'

    reg_date = forms.ChoiceField(
        label='Termín zápisu',
        help_text='Vybraný termín bude rezervován až po odeslání tohoto formuláře.',
        error_messages=dict(invalid_choice=ERR_MSG_UNAVAILABLE_REG_DATE),
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = [
            'child_name',
            'child_birth_date',
            'address',
            'parent_name',
            'phone',
            'email',
            'possible_postponement',
            'reg_date',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        available_dates = RegistrationDate.objects.filter(
            date__gt=timezone.now(),
        ).exclude(
            id__in=RegistrationAnswer.objects.filter(reg_date__isnull=False).values('reg_date')
        ).values_list(
            'pk',
            'date',
        ).distinct()
        choices = [
            (pk, date.strftime('%d.%m.%Y %H:%M'))
            for (pk, date) in available_dates
        ]
        if choices:
            self.fields['reg_date'].choices = [('', '-- Vyberte termín --')] + choices

    def is_open(self):
        return bool(
            self.fields['reg_date'].choices
        )

    def clean_reg_date(self):
        try:
            reg_date = RegistrationDate.objects.filter(
                id=self.cleaned_data['reg_date']
            ).exclude(
                id__in=RegistrationAnswer.objects.filter(reg_date__isnull=False).values('reg_date')
            ).get()
        except RegistrationDate.DoesNotExist:
            raise forms.ValidationError(
                self.ERR_MSG_UNAVAILABLE_REG_DATE,
                code='invalid_choice'
            )

        return reg_date

    def clean(self):
        cd = super().clean()
        child_name = cd.get('child_name', '').strip()
        child_birth_date = cd.get('child_birth_date', '')

        if child_name and child_birth_date:
            # Potreba zabranit opakovanym registracim.
            # Stejne jmeno a datum narozeni se muze opakovat (napr. odklad
            # o rok), takze je potrebne dat urcity casovy odstup.
            is_duplicate = RegistrationAnswer.objects.filter(
                child_name=child_name,
                child_birth_date=child_birth_date,
                created__gt=timezone.now() - datetime.timedelta(days=90)
            )
            if is_duplicate:
                raise forms.ValidationError(
                    mark_safe(
                        f'Registrace s tímto jménem a datem narození již byla '
                        f'provedena. Pokud potřebujete změnit termín, '
                        f'nebo cokoliv jiného, <a href="{settings.CONTACT_URL}">kontaktujte nás</a> '
                        f'prosím.'
                    ),
                    code='duplicate_registration'
                )

        return cd

    def save(self) -> RegistrationAnswer:  # type: ignore[override]  # pylint: disable=W0221
        answers_count = RegistrationAnswer.objects.filter(
            identifier__startswith=settings.REG_IDENTIFIER_PREFIX,
        ).count() + 1
        obj = super().save(commit=False)
        obj.identifier = f"{settings.REG_IDENTIFIER_PREFIX}{answers_count:02d}"
        try:
            obj.save()
            return obj
        except IntegrityError as exc:
            self.add_error(
                'reg_date',
                forms.ValidationError(
                    self.ERR_MSG_UNAVAILABLE_REG_DATE,
                    code='invalid_choice',
                )
            )
            raise RegistrationFailedException() from exc


class SubstituteContactForm(BaseRegistrationForm):

    class Meta(BaseRegistrationForm.Meta):
        fields = [
            'child_name',
            'child_birth_date',
            'address',
            'parent_name',
            'phone',
            'email',
            'possible_postponement',
        ]

    def save(self):  # type: ignore[override]  # pylint: disable=W0221
        obj = super().save(commit=False)
        obj.substitute = True
        obj.identifier = None
        obj.save()
        return obj
