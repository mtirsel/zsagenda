
import datetime
from django.conf import settings
from django.test import TestCase

from model_bakery import baker

from regform.forms import RegistrationAnswerForm
from regform.models import RegistrationAnswer, RegistrationDate



class TestRegistrationAnswerForm(TestCase):
    def test_form_creates_registration_answer(self):
        reg_date_obj = baker.make(
            RegistrationDate,
            date=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        form = RegistrationAnswerForm(
            data={
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

        self.assertTrue(form.is_valid())
        reg_obj = form.save()
        self.assertIsNotNone(reg_obj)
        self.assertEqual(reg_obj.email, 'foo@bar.baz')
        self.assertEqual(reg_obj.child_name, 'Foo Bar')
        self.assertEqual(reg_obj.parent_name, 'Bar Foo')
        self.assertEqual(
            reg_obj.child_birth_date,
            datetime.date(2013, 4, 15)
        )
        self.assertEqual(reg_obj.phone, '123456789')
        self.assertEqual(reg_obj.address, 'Foo 123, Bar')
        self.assertEqual(reg_obj.possible_postponement, 20)
        self.assertEqual(reg_obj.reg_date, reg_date_obj)
        self.assertEqual(reg_obj.identifier, f'{settings.REG_IDENTIFIER_PREFIX}01')

    def test_form_invalid_when_no_available_reg_dates(self):
        reg_date_obj = baker.make(
            RegistrationDate,
            date=datetime.datetime.now() - datetime.timedelta(days=5)
        )
        baker.make(
            RegistrationAnswer,
            reg_date=reg_date_obj,
        )
        form = RegistrationAnswerForm(
            data={
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

        self.assertFalse(form.is_valid())
        self.assertIn('reg_date', form.errors)
