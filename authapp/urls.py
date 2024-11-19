# authapp/urls.py

from django.urls import path
from .views import AuthenticateView, SignupView

urlpatterns = [
    path('login/', AuthenticateView.as_view(), name='authenticate'),
    path('signup/', SignupView.as_view(), name='signup')
]
