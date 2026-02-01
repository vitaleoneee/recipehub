from django.urls import path
from allauth.account import views as allauth_views

from recipehub.apps.users import views

urlpatterns = [
    path("login/", allauth_views.LoginView.as_view(), name="account_login"),
    path("logout/", allauth_views.LogoutView.as_view(), name="account_logout"),
    path("signup/", allauth_views.SignupView.as_view(), name="account_signup"),
    # Password change
    path(
        "password/change/",
        allauth_views.PasswordChangeView.as_view(),
        name="account_change_password",
    ),
    # Password reset
    path(
        "password/reset/",
        allauth_views.PasswordResetView.as_view(),
        name="account_reset_password",
    ),
    path(
        "password/reset/done/",
        allauth_views.PasswordResetDoneView.as_view(),
        name="account_reset_password_done",
    ),
    path(
        "password/reset/key/<uidb36>-<key>/",
        allauth_views.PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path(
        "password/reset/key/done/",
        allauth_views.PasswordResetFromKeyDoneView.as_view(),
        name="account_reset_password_from_key_done",
    ),
    # Confirm email
    path(
        "confirm-email/",
        allauth_views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent",
    ),
    path(
        "confirm-email/<key>/",
        allauth_views.ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    # Other
    path("profile/", views.profile, name="profile"),
    path(
        "profile-edit/<int:pk>", views.ProfileUpdateView.as_view(), name="profile-edit"
    ),
    path("saved-recipes", views.saved_recipes, name="saved-recipes"),
    path("remove-saved-recipe/", views.remove_saved_recipe, name="remove_saved_recipe"),
]
