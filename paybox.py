import random
import string
from hashlib import md5
from typing import Tuple
from urllib.parse import urlencode

from django.urls import reverse_lazy
from django.conf import settings
from django.urls.base import reverse


class PayboxPaymentService:
    """
        Paybox service which is returning and creating paybox
        payment url.
    """

    @staticmethod
    def get_merchant_id_and_secret_key() -> Tuple[str, str]:
        merchant_id = settings.PAYBOX_MERCHANT_ID
        secret_key = settings.PAYBOX_SECRET_KEY
        return str(merchant_id), secret_key

    @staticmethod
    def get_salt() -> str:
        letters = string.ascii_letters
        pg_salt = ''.join(random.choice(letters) for _ in range(10))
        return str(pg_salt)

    @staticmethod
    def get_pg_sig(query_params: dict, secret_key: str) -> str:
        sort = sorted(query_params.items())
        result = []
        for i in sort:
            result.append(i[1])
        result.insert(0, 'init_payment.php')
        result.append(secret_key)
        pg_sig = ';'.join(result)
        pg_sig = md5(pg_sig.encode('UTF-8')).hexdigest()
        return pg_sig

    def get_payment_body(self, order, request):
        pg_result_url = str(request.build_absolute_uri())
        pg_result_url = pg_result_url.replace(
            request.path_info, str(reverse_lazy('get_payment_response')
                                   ))
        pg_success_url = request.build_absolute_uri(reverse('shop-page'))
        merchant_id, secret_key = self.get_merchant_id_and_secret_key()
        pg_salt = self.get_salt()
        # TODO: All query params you can find and select in the official paybox documentation page
        query_params = {
            'pg_merchant_id': merchant_id,
            'pg_amount': str(order.get_total_cost()),
            'pg_currency': 'KGS',
            'pg_description': 'something cool here',
            'pg_salt': pg_salt,
            'pg_language': 'ru',
            'pg_order_id': str(order.id),
            'pg_result_url': pg_result_url,
            'pg_success_url': pg_success_url,
            'pg_success_url_method': 'GET',
            'pg_request_method': 'GET',
            'pg_user_phone': order.phone_number,
            'first_name': order.first_name,
            'last_name': order.last_name,
        }
        query_params['pg_sig'] = self.get_pg_sig(query_params, secret_key)
        url_params = urlencode(query_params)
        url = settings.PAYBOX_URL
        url += 'init_payment.php' + '?' + url_params
        return url
