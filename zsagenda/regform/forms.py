
import datetime

from django import forms
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.utils.safestring import mark_safe

from regform.models import RegistrationAnswer
from regform.models import RegistrationDate
from regform.models import SubstituteContact


class BaseRegistrationForm(forms.ModelForm):
    class Meta:
        model = RegistrationAnswer
        fields = []
        widgets = {
            'possible_postponement': forms.widgets.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove default choice
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
            'date',
            flat=True
        ).distinct()
        available_dates = [
            d.strftime('%d.%m.%Y %H:%M') for d in available_dates
        ]
        choices = [
            (d, d)
            for d in available_dates
        ]
        if choices:
            self.fields['reg_date'].choices = [('', '-- Vyberte termín --')] + choices

    def is_open(self):
        return bool(
            self.fields['reg_date'].choices
        )

    def clean_reg_date(self):
        try:
            parsed_date = datetime.datetime.strptime(
                self.cleaned_data['reg_date'],
                '%d.%m.%Y %H:%M'
            )
        except ValueError:
            raise forms.ValidationError(
                'Nesprávný formát termínu.',
                code='invalid_format'
            )

        reg_date = RegistrationDate.objects.filter(
            date__date=parsed_date
        ).exclude(
            id__in=RegistrationAnswer.objects.filter(reg_date__isnull=False).values('reg_date')
        ).first()
        if reg_date is None:
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
                        'Registrace s tímto jménem a datem narození již byla '
                        'provedena. Pokud potřebujete změnit termín, '
                        'nebo cokoliv jiného, <a href="%s">kontaktujte nás</a> '
                        'prosím.' % (
                            settings.CONTACT_URL,
                        )
                    ),
                    code='duplicate_registration'
                )

        return cd

    def save(self):
        cd = self.cleaned_data
        reg_date = cd['reg_date']
        obj = super().save(commit=False)
        obj.reg_date = reg_date
        # we need thist to satisfy the condition for count below
        obj.identifier = settings.REG_IDENTIFIER_PREFIX
        try:
            obj.save()
        except IntegrityError:
            self.add_error(
                'reg_date',
                forms.ValidationError(
                    self.ERR_MSG_UNAVAILABLE_REG_DATE,
                    code='invalid_choice',
                )
            )
            return

        obj.identifier = '%s%02d' % (
            settings.REG_IDENTIFIER_PREFIX,
            RegistrationAnswer.objects.filter(
                identifier__startswith=settings.REG_IDENTIFIER_PREFIX,
            ).count()
        )
        obj.save()

        return obj


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

    def save(self):
        cd = self.cleaned_data
        obj = super().save(commit=False)
        obj.substitute = True
        # we need thist to satisfy the condition for count below
        obj.identifier = None
        obj.save()
        return obj
