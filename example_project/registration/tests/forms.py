from django.contrib.auth.models import User
from django.test import TestCase

from registration import forms


class RegistrationFormTests(TestCase):
    """
    Test the default registration forms.

    """
    def test_registration_form(self):
        """
        Test that ``RegistrationForm`` enforces username constraints
        and matching passwords.

        """
        # Create a user so we can verify that duplicate usernames aren't
        # permitted.
        User.objects.create_user('alice', 'alice@example.com', 'secret')

        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username': 'foo/bar',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'foo'},
            'error': ('username', [u"This value must contain only letters, numbers and underscores."])},
            # Already-existing username.
            {'data': {'username': 'alice',
                      'email': 'alice@example.com',
                      'password1': 'secret',
                      'password2': 'secret'},
            'error': ('username', [u"A user with that username already exists."])},
            # Mismatched passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'bar'},
            'error': ('__all__', [u"The two password fields didn't match."])},
            ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        form = forms.RegistrationForm(data={'username': 'foo',
                                            'email': 'foo@example.com',
                                            'password1': 'foo',
                                            'password2': 'foo'})
        self.failUnless(form.is_valid())

    def test_registration_form_tos(self):
        """
        Test that ``RegistrationFormTermsOfService`` requires
        agreement to the terms of service.

        """
        form = forms.RegistrationFormTermsOfService(data={'username': 'foo',
                                                          'email': 'foo@example.com',
                                                          'password1': 'foo',
                                                          'password2': 'foo'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['tos'],
                         [u"You must agree to the terms to register"])

        form = forms.RegistrationFormTermsOfService(data={'username': 'foo',
                                                          'email': 'foo@example.com',
                                                          'password1': 'foo',
                                                          'password2': 'foo',
                                                          'tos': 'on'})
        self.failUnless(form.is_valid())

    def test_registration_form_unique_email(self):
        """
        Test that ``RegistrationFormUniqueEmail`` validates uniqueness
        of email addresses.

        """
        # Create a user so we can verify that duplicate addresses
        # aren't permitted.
        User.objects.create_user('alice', 'alice@example.com', 'secret')

        form = forms.RegistrationFormUniqueEmail(data={'username': 'foo',
                                                       'email': 'alice@example.com',
                                                       'password1': 'foo',
                                                       'password2': 'foo'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['email'],
                         [u"This email address is already in use. Please supply a different email address."])

        form = forms.RegistrationFormUniqueEmail(data={'username': 'foo',
                                                       'email': 'foo@example.com',
                                                       'password1': 'foo',
                                                       'password2': 'foo'})
        self.failUnless(form.is_valid())

    def test_registration_form_no_free_email(self):
        """
        Test that ``RegistrationFormNoFreeEmail`` disallows
        registration with free email addresses.

        """
        base_data = {'username': 'foo',
                     'password1': 'foo',
                     'password2': 'foo'}
        for domain in forms.RegistrationFormNoFreeEmail.bad_domains:
            invalid_data = base_data.copy()
            invalid_data['email'] = u"foo@%s" % domain
            form = forms.RegistrationFormNoFreeEmail(data=invalid_data)
            self.failIf(form.is_valid())
            self.assertEqual(form.errors['email'],
                             [u"Registration using free email addresses is prohibited. Please supply a different email address."])

        base_data['email'] = 'foo@example.com'
        form = forms.RegistrationFormNoFreeEmail(data=base_data)
        self.failUnless(form.is_valid())
