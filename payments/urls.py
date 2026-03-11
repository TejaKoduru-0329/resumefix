from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_page, name='payment_page'),
    path("add-credits/", views.add_credits, name="add_credits"),
]