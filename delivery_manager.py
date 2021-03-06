from flask import url_for
from flask_mail import Message
from app import create_app, mail
from app.models import Delivery, Price
from datetime import datetime


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        # Получение активных рассылок
        deliveries = Delivery.objects(enabled=True, expires_at__gt=datetime.now())

        with mail.connect() as conn:
            for delivery in deliveries:
                # Получение автомобилей для рассылки
                automobiles = Price.objects.filter(
                    automobile_props__manufacturer=delivery.manufacturer,
                    automobile_props__model=delivery.model,
                    automobile_props__year__gte=delivery.year_from,
                    automobile_props__year__lte=delivery.year_to,
                    value__lte=delivery.price_to,
                    value__gte=delivery.price_from,
                    created_at__gte=delivery.last_letter_at
                )
                if delivery.transmission:
                    automobiles = automobiles.filter(automobile_props__transmission=delivery.transmission)

                # Формирование письма и его отправка
                if automobiles:
                    msg = Message("{} {}".format(delivery.manufacturer, delivery.model),
                                  recipients=[delivery.user_id.email])
                    msg.html = '<b>Добрый день, {}!</b>'.format(delivery.user_id.username)
                    msg.html += '<p></p>'
                    msg.html += '<p>Обнаружены следующие объявления на сайте e1.auto.ru:</p>'
                    msg.html += '<ol>'
                    for auto in automobiles:
                        msg.html += '<li><b>{} {} {} г.в.</b> ({} руб.) Ссылка на {}. Ссылка на {}.</li>'.format(
                            auto.automobile.props['manufacturer'],
                            auto.automobile.props['model'],
                            auto.automobile.props['Год выпуска'],
                            auto.value,
                            '<a href="https://auto.e1.ru/car/used/manufacturer/model/{}">auto.e1.ru</a>'.format(
                                auto.automobile.e1_id
                            ),
                            '<a href="{}">{}</a>'.format(
                                url_for('automobile.index', auto_id=auto.automobile.id),
                                app.config['SERVER_NAME']
                            )
                        )
                    msg.html += '</ol>'
                    conn.send(msg)
                    Delivery.objects(id=delivery.id).update_one(set__last_letter_at=datetime.now())
