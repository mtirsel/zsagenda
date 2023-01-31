from django.contrib import admin

from regform.models import RegistrationDate
from regform.models import RegistrationAnswer
from regform.models import SubstituteContact


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
        'substitute',
        'identifier',
        'email',
        'email_sent',
        'child_name',
        'parent_name',
        'child_birth_date',
        'phone',
        'address',
        'get_possible_postponement',
        'note',
        'created',
        'modified',
    )
    list_filter = (
        'substitute',
    )

    def get_possible_postponement(self, obj):
        return obj.get_possible_postponement_display()
    get_possible_postponement.short_description = 'Uvažuje o odkladu'

admin.site.register(RegistrationAnswer, RegistrationAnswerAdmin)


# class SubstituteContactAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'email',
#         'phone',
#         'created',
#         'modified',
#     )

# admin.site.register(SubstituteContact, SubstituteContactAdmin)
