from flask import Blueprint, request, current_app
from hashlib import sha1
from decimal import Decimal
from app.models import Order
from app import csrf


billing = Blueprint('billing', __name__)


class YandexMoneyHash:
    """
    Integrity check for Yandex.Money HTTP-notifications
    Usage example:
    yahash = YandexMoheyHash(request.POST, settings.YANDEX_MONEY_SECRET)
    if yahash.check(request.POST['sha1_hash']):
        # process invoice
    """

    def __init__(self, query, secret):
        self.secret = secret
        self.hash_str = self.make_hash_str(query)

    def make_hash_str(self, query):
        hash_str = ''
        keys = ['notification_type', 'operation_id', 'amount',
                'currency', 'datetime', 'sender', 'codepro', 'label']
        for key in keys:
            value = query[key]
            if key == 'label':
                hash_str += self.secret + '&' + value
                continue
            hash_str += value + '&'
        return hash_str

    def make(self):
        return sha1(bytes(self.hash_str, 'utf-8')).hexdigest()

    def check(self, check):
        return self.make() == check


@csrf.exempt
@billing.route('/billing/confirm/', methods=['POST'])
def index():
    """Обрабатывает POST-запрос от сервиса Яндекс.Деньги."""
    yahash = YandexMoneyHash(request.form, current_app.config.get('YANDEX_MONEY_SECRET'))
    # Проверка на подлинность запроса
    if yahash.check(request.form['sha1_hash']):
        if request.form['label']:
            order = Order.objects(id=request.form['label']).first()
            if order and not order.paid_at:
                # Проверка на соответствие суммы
                if float(request.form['withdraw_amount']) < order.sum:
                    return 'INVALID_AMOUNT', 400

                # Пометка заказа как оплаченного и изменение баланса юзера
                order.mark_paid()
                order.user.balance += Decimal(request.form['withdraw_amount'])
                order.user.save()
                return 'OK', 200

    return 'INVALID_REQUEST', 400
