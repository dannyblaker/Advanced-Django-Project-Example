from django.urls import path
from .views import not_available_in_your_country, affiliates, signup

urlpatterns = [
    path('', signup, name='signup'),
    path('affiliates/', affiliates, name='affiliates'),
    path('currently-unavailable/', not_available_in_your_country, name='not_available_in_your_country'),
]