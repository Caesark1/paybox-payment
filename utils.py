import requests

import xml.etree.ElementTree as ET

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.base import ModelBase

from paybox import PayboxPaymentService


paybox_service = PayboxPaymentService()


def send_request_and_get_paybox_payment_url(order: ModelBase, request: WSGIRequest) -> str:
    response = requests.get(paybox_service.get_payment_body(order, request))
    root = ET.fromstring(response.text)
    payment_url = root.find('pg_redirect_url').text
    return payment_url
