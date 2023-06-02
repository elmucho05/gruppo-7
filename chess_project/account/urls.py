from django.urls import path

from . import views

urlpatterns = [
  # http://127.0.0.1:8000/account
  path("", views.ViewAccount.as_view(), name="view_account"),
]
