
import datetime
from django.test import TestCase

from django.urls import reverse
from model_bakery import baker

from regform.models import RegistrationAnswer, RegistrationDate


class TestRegistrationAnswerForm(TestCase):
    def test_form_creates_registration_answer(self):
        reg_date_obj = baker.make(
            RegistrationDate,
            date=datetime.datetime.now() + datetime.timedelta(days=5)
        )

        result = self.client.post(
            reverse('display_form'),
            {
                'reg_date': reg_date_obj.pk,
                'email': 'foo@bar.baz',
                'child_name': 'Foo Bar',
                'parent_name': 'Bar Foo',
                'child_birth_date': '2013-04-15',
                'phone': '123456789',
                'address': 'Foo 123, Bar',
                'possible_postponement': 20,
            }
        )
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, reverse('registration_done'))

        self.assertEqual(RegistrationAnswer.objects.count(), 1)
        db_answer = RegistrationAnswer.objects.first()
        self.assertEqual(db_answer.reg_date, reg_date_obj)

    def test_form_invalid_when_no_available_reg_dates(self):
        pass
