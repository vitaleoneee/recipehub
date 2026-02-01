import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from recipehub.apps.users.forms import CustomSignupForm
from django import forms


@pytest.mark.django_db
class TestCustomSignupForm:
    """Tests for CustomSignupForm"""

    def test_form_has_all_required_fields(self):
        """Checking if all fields in a form are present"""
        form = CustomSignupForm()
        assert "username" in form.fields
        assert "email" in form.fields
        assert "password1" in form.fields
        assert "password2" in form.fields
        assert "date_of_birth" in form.fields
        assert "photo" in form.fields

    def test_field_order_is_correct(self):
        """Checking field order"""
        form = CustomSignupForm()
        expected_order = [
            "username",
            "password1",
            "password2",
            "email",
            "photo",
            "date_of_birth",
        ]
        assert form.field_order == expected_order

    def test_date_of_birth_is_optional(self):
        """Date of birth is optional"""
        form = CustomSignupForm()
        assert form.fields["date_of_birth"].required is False

    def test_photo_is_optional(self):
        """Photo optional"""
        form = CustomSignupForm()
        assert form.fields["photo"].required is False

    def test_date_of_birth_widget_type(self):
        """Checking the widget type for the date of birth"""
        form = CustomSignupForm()
        assert isinstance(form.fields["date_of_birth"].widget, forms.DateInput)

    def test_photo_widget_is_file_input(self):
        """Testing the Photo Widget"""
        form = CustomSignupForm()
        assert isinstance(form.fields["photo"].widget, forms.FileInput)

    def test_valid_form_with_minimal_data(self, valid_signup_data):
        """The form is valid with minimal data (no optional fields)"""
        form = CustomSignupForm(data=valid_signup_data)
        assert form.is_valid()

    def test_valid_form_with_all_data(self, valid_signup_data, sample_image):
        """The form is valid with all data"""
        data = valid_signup_data.copy()
        data["date_of_birth"] = "1990-01-01"
        form = CustomSignupForm(data=data, files={"photo": sample_image})
        assert form.is_valid()

    def test_invalid_form_missing_username(self, valid_signup_data):
        """The form is invalid without username"""
        data = valid_signup_data.copy()
        del data["username"]
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_invalid_form_missing_email(self, valid_signup_data):
        """The form is invalid without email"""
        data = valid_signup_data.copy()
        del data["email"]
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_form_missing_password1(self, valid_signup_data):
        """The form is invalid without a password1"""
        data = valid_signup_data.copy()
        del data["password1"]
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "password1" in form.errors

    def test_invalid_form_missing_password2(self, valid_signup_data):
        """The form is invalid without a password2"""
        data = valid_signup_data.copy()
        del data["password2"]
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_invalid_form_passwords_dont_match(self, valid_signup_data):
        """The form is invalid if the passwords do not match"""
        data = valid_signup_data.copy()
        data["password2"] = "DifferentPass123!"
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_invalid_email_format(self, valid_signup_data):
        """The form is invalid due to an invalid email address"""
        data = valid_signup_data.copy()
        data["email"] = "invalid-email"
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_date_of_birth_format(self, valid_signup_data):
        """The form is invalid due to incorrect date format"""
        data = valid_signup_data.copy()
        data["date_of_birth"] = "invalid-date"
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "date_of_birth" in form.errors

    def test_future_date_of_birth(self, valid_signup_data):
        """The form accepts a future date (if there is no validation)"""
        data = valid_signup_data.copy()
        future_date = date.today() + timedelta(days=365)
        data["date_of_birth"] = future_date.strftime("%Y-%m-%d")
        form = CustomSignupForm(data=data)
        assert form.is_valid()

    def test_invalid_photo_file_type(self, valid_signup_data):
        """The form is invalid due to the wrong file type"""
        data = valid_signup_data.copy()
        invalid_file = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain"
        )
        form = CustomSignupForm(data=data, files={"photo": invalid_file})
        assert not form.is_valid()
        assert "photo" in form.errors

    def test_duplicate_username(self, valid_signup_data, django_user_model):
        """The form is invalid when the username is duplicated"""
        django_user_model.objects.create_user(
            username="testuser", email="other@example.com", password="pass123"
        )

        form = CustomSignupForm(data=valid_signup_data)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_weak_password(self, valid_signup_data):
        """The form is invalid with a weak password"""
        data = valid_signup_data.copy()
        data["password1"] = "123"
        data["password2"] = "123"
        form = CustomSignupForm(data=data)
        assert not form.is_valid()
        assert "password1" in form.errors

    def test_form_labels(self):
        """Checking field labels"""
        form = CustomSignupForm()
        assert form.fields["date_of_birth"].label == "Date of Birth (optional)"
        assert form.fields["photo"].label == "Photo (optional)"

    def test_cleaned_data_contains_all_fields(self, valid_signup_data, sample_image):
        """Checking that cleaned_data contains all fields"""
        data = valid_signup_data.copy()
        data["date_of_birth"] = "1990-01-01"
        form = CustomSignupForm(data=data, files={"photo": sample_image})
        assert form.is_valid()

        assert "username" in form.cleaned_data
        assert "email" in form.cleaned_data
        assert "password1" in form.cleaned_data
        assert "date_of_birth" in form.cleaned_data
        assert "photo" in form.cleaned_data
