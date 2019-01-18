from django.contrib import admin

from regform.models import RegistrationDate
from regform.models import RegistrationAnswer


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

admin.site.register(RegistrationAnswer, RegistrationAnswerAdmin)
