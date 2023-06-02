from django.urls import path

from . import views

urlpatterns = [
  # http://127.0.0.1:8000/authentication/login
  path("login/", views.ViewLogin.as_view(), name="view_login"),

  # http://127.0.0.1:8000/authentication/signup
  path("sign-up/", views.ViewSignUp.as_view(), name="view_signup"),

  # http://127.0.0.1:8000/authentication/logout
  path("logout/", views.view_logout, name="view_logout"),
]