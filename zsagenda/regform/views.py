
import datetime
import smtplib
import socket

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone

from regform.forms import RegistrationAnswerForm
from regform.forms import SubstituteContactForm
from regform.models import RegistrationAnswer
from regform.models import RegistrationDate
from regform.utils import send_registration_email


def display_form(request):
    form = RegistrationAnswerForm(request.POST or None)

    if not form.is_open():
        if request.method == 'POST':
            messages.error(
                request,
                'Registrace nebyla provedena z důvodu vyčerpání volných míst. '
                'Můžeme Vás zaevidovat jako náhradníky, stačí formulář níže znovu odeslat.'
            )
            return registration_closed(request, rerouted=True)
        return redirect('registration_closed')

    if form.is_valid():
        reg_obj = form.save()
        if form.is_valid():
            messages.success(
                request,
                'Registrace k zápisu byla úspěšně provedena pod evidenčním číslem %s.' % (
                    reg_obj.identifier,
                )
            )

            try:
                send_registration_email(reg_obj)
            except (smtplib.SMTPException, socket.gaierror, TimeoutError):
                messages.warning(
                    request,
                    mark_safe(
                        'Při odesílání e-mailu došlo k chybě a e-mail se Vám bohužel '
                        'nepodařilo odeslat. Nemusíte mít obavy, registrace '
                        'je platná pod výše uvedeným evidenčním číslem. V případě '
                        'nejasností nás můžete <a href="%s">kontaktovat</a>.' % (
                            settings.CONTACT_URL,
                        )
                    )
                )

            return redirect('registration_done')

    today = datetime.date.today()
    if 12 >= today.month >= 9:
        school_year = '%s/%s' % (today.year + 1, today.year + 2)
    else:
        school_year = '%s/%s' % (today.year, today.year + 1)

    return render(
        request,
        'registration_form.html',
        dict(
            form=form,
            school_year=school_year
        ),
    )


def registration_closed(request, rerouted=False):
    form = SubstituteContactForm(request.POST or None)
    if form.is_valid() and not rerouted:
        form.save()
        messages.success(
            request,
            'Registrovali jsme Vás jako náhradníky, v případě uvolnění místa Vás budeme kontaktovat.'
        )
        return HttpResponseRedirect(
            '%s?kontakt-odeslan' % reverse('registration_closed')
        )
    return render(
        request,
        'registration_closed.html',
        dict(
            form=form,
        )
    )


def registration_done(request):
    return render(
        request,
        'registration_done.html',
        dict()
    )


def is_registration_open(request):
    if settings.FORCE_REPORT_OPEN:
        is_open = True
    else:
        is_open = RegistrationDate.objects.filter(
            date__gt=timezone.now(),
        ).exclude(
            id__in=RegistrationAnswer.objects.all().values('reg_date')
        ).exists()

    response = JsonResponse(
        dict(
            is_open=is_open,
        )
    )
    if hasattr(settings, 'REG_API_ALLOW_ORIGIN'):
        response['Access-Control-Allow-Origin'] = settings.REG_API_ALLOW_ORIGIN
    return response
