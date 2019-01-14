
import datetime
import smtplib
import socket

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from regform.forms import RegistrationAnswerForm


def display_form(request):
    form = RegistrationAnswerForm(request.POST or None)

    if not form.is_open():
        if request.method == 'POST':
            messages.error(
                request,
                'Registrace nebyla provedena z důvodu vyčerpání volných míst.'
            )
        return redirect('registration_closed')

    if form.is_valid():
        reg_obj = form.save()
        messages.success(
            request,
            'Registrace k zápisům byla úspěšně provedena pod evidenčním číslem %d.' % (
                reg_obj.identifier,
            )
        )

        msg_plain = render_to_string(
            'mail/registration_confirmation.txt',
            dict(
                reg_obj=reg_obj,
            )
        )

        email = EmailMessage(
            subject='Potvrzení o registraci k zápisům',
            body=msg_plain,
            from_email=settings.REG_FORM_EMAIL_SENDER,
            to=[
                reg_obj.email,
            ],
            cc=settings.REG_FORM_EMAIL_CC,
        )

        try:
            email.send()
        except (smtplib.SMTPException, socket.gaierror):
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
        else:
            reg_obj.email_sent = True
            reg_obj.save()

        return redirect('registration_done')

    today = datetime.date.today()
    if 12 >= today.month >= 9:
        school_year = '%s/%s' % (today.year + 1, today.year)
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


def registration_closed(request):
    return render(
        request,
        'registration_closed.html',
        dict()
    )


def registration_done(request):
    return render(
        request,
        'registration_done.html',
        dict()
    )
