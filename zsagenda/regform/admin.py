
import smtplib
import socket

from django.contrib import admin
from django.contrib import messages

from regform.models import RegistrationDate
from regform.models import RegistrationAnswer
from regform.models import SubstituteContact
from regform.utils import send_registration_email


class RegistrationDateAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'get_availability',
    )
    save_as = True

    def get_availability(self, obj):
        return obj.is_available()
    get_availability.boolean = True
    get_availability.short_description = 'Termín je volný'

admin.site.register(RegistrationDate, RegistrationDateAdmin)


class RegistrationAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'reg_date',
        'identifier',
        'email',
        'email_sent',
        'child_name',
        'parent_name',
        'child_birth_date',
        'phone',
        'address',
        'note',
        'created',
        'modified',
    )
    actions = ['resend_registration_email']

    def resend_registration_email(self, request, queryset):
        for obj in queryset:
            try:
                send_registration_email(obj)
            except (smtplib.SMTPException, socket.gaierror, TimeoutError):
                self.message_user(
                    request,
                    message="Při odesílání e-mailu s adresou %s došlo k chybě." % obj.email,
                    level=messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    message="E-mail %s úspěšně odeslán." % obj.email,
                    level=messages.SUCCESS
                )
    resend_registration_email.short_description = 'Odeslat registační e-mail'

admin.site.register(RegistrationAnswer, RegistrationAnswerAdmin)


class SubstituteContactAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'phone',
        'created',
        'modified',
    )

admin.site.register(SubstituteContact, SubstituteContactAdmin)
