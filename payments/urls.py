# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("paypal/capture/<int:transaction_id>/", views.paypal_capture, name="paypal_capture"),
    path("momo/webhook/", views.momo_webhook, name="momo_webhook"),
]