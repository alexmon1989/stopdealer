from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_security import login_required, current_user
from flask_security.utils import encrypt_password
from .forms import DetailsForm, CheapenedAutosForm, DeliveryForm, BillingForm, TariffForm
from app.models import CheapenedAuto, Delivery, Order, Tariff
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

cabinet = Blueprint('cabinet', __name__)


@cabinet.route('/cabinet/details/', methods=['GET', 'POST'])
@login_required
def details():
    """Отображает страницу Детали"""
    form = DetailsForm(request.form, meta={'locales': ['ru_RU', 'ru']})

    if request.method == 'POST' and form.validate():
        current_user.username = form.username.data
        if form.password.data:
            current_user.password = encrypt_password(form.password.data)
        current_user.save()
        flash('Данные успешно сохранены!')
        return redirect(url_for('cabinet.details'))

    return render_template("cabinet/details.html",
                           form=form)


@cabinet.route('/cabinet/cheapened_autos/', defaults={'page': 1})
@cabinet.route('/cabinet/cheapened_autos/page/<int:page>/')
@login_required
def cheapened_autos(page=1):
    """Отображает страницу Подешевевшие авто"""
    form = CheapenedAutosForm(request.form,
                              meta={'locales': ['ru_RU', 'ru']})
    # Заполнение полей формы
    form.manufacturer.choices = [('', '')]
    manufacturers = CheapenedAuto.objects.distinct(field='automobile.props.manufacturer')
    form.manufacturer.choices.extend([(x, x) for x in sorted(manufacturers)])
    form.manufacturer.default = request.args.get('manufacturer')
    form.model.choices = [('', '')]
    if request.args.get('manufacturer'):
        models = CheapenedAuto.objects(automobile__props__manufacturer=request.args.get('manufacturer'))\
            .distinct(field='automobile.props.model')
        form.model.choices.extend([(x, x) for x in sorted(models)])
        form.model.default = request.args.get('model')
    form.year_from.choices = [('', '')]
    form.year_from.choices.extend([(x, x) for x in range(date.today().year, 1899, -1)])
    form.year_from.default = request.args.get('year_from')
    form.year_to.choices = [('', '')]
    form.year_to.choices.extend([(x, x) for x in range(date.today().year, 1899, -1)])
    form.year_to.default = request.args.get('year_to')
    form.fell_by_from.default = request.args.get('fell_by_from')
    form.fell_by_to.default = request.args.get('fell_by_to')
    form.fell_by_date_from.default = request.args.get('fell_by_date_from')
    form.fell_by_date_to.default = request.args.get('fell_by_date_to')
    form.process()

    # Список подешевевших авто для отображения
    autos = CheapenedAuto.objects
    if request.args.get('manufacturer'):
        autos = autos.filter(automobile__props__manufacturer=request.args.get('manufacturer'))
    if request.args.get('model'):
        autos = autos.filter(automobile__props__model=request.args.get('model'))
    if request.args.get('year_from'):
        autos = autos.filter(automobile__props__year__gte=int(request.args.get('year_from')))
    if request.args.get('year_to'):
        autos = autos.filter(automobile__props__year__lte=int(request.args.get('year_to')))
    if request.args.get('fell_by_from'):
        autos = autos.filter(fell_by__gte=request.args.get('fell_by_from'))
    if request.args.get('fell_by_to'):
        autos = autos.filter(fell_by__lte=request.args.get('fell_by_to'))
    if request.args.get('fell_by_date_from'):
        autos = autos.filter(created_at__gte=datetime.strptime(request.args.get('fell_by_date_from'), '%d.%m.%Y'))
    if request.args.get('fell_by_date_to'):
        date_to = datetime.strptime(request.args.get('fell_by_date_to'), '%d.%m.%Y') + timedelta(days=1)
        autos = autos.filter(created_at__lte=date_to)
    autos = autos.order_by('-created_at').paginate(page=page, per_page=10)

    # Отображение страницы
    return render_template("cabinet/cheapened_autos.html",
                           form=form,
                           cheapened_autos=autos,
                           page=page)


@cabinet.route('/cabinet/cheapened_autos/get-models/<string:manufacturer>/')
def get_models(manufacturer):
    return jsonify(sorted(CheapenedAuto.objects(automobile__props__manufacturer=manufacturer)
                          .distinct(field='automobile.props.model')))


@cabinet.route('/cabinet/deliveries/page/')
@login_required
def deliveries():
    """Отображает страницу Рассылки"""
    deliveries_list = Delivery.objects(user_id=current_user.get_id()).order_by('-created_at')

    # Отображение страницы
    return render_template("cabinet/deliveries/index.html",
                           deliveries=deliveries_list,
                           deliveries_count=len(deliveries_list))


@cabinet.route('/cabinet/deliveries/create', methods=['GET', 'POST'])
def create_delivery():
    """Отображает страницу создания рассылки, обрабатывает POST-запроса на создание рассылки"""
    # Если у пользователя 10 и больше рассылок, то запрет на создание
    if len(Delivery.objects(user_id=current_user.get_id())) > 9:
        flash('Невозможно создать рассылку, т.к. у вас есть 10 созданных рассылок. '
              'Для создания новой удалите одну или более из "старых" рассылок.')
        return redirect(url_for('cabinet.deliveries'))

    form = DeliveryForm(request.form, meta={'locales': ['ru_RU', 'ru']})
    # Заполнение полей формы
    form.manufacturer.choices = [('', '')]
    manufacturers = CheapenedAuto.objects.distinct(field='automobile.props.manufacturer')
    form.manufacturer.choices.extend([(x, x) for x in sorted(manufacturers)])
    form.manufacturer.default = request.args.get('manufacturer')
    form.model.choices = [('', '')]
    if form.model.data:
        models = CheapenedAuto.objects(automobile__props__manufacturer=form.manufacturer.data)\
            .distinct(field='automobile.props.model')
        form.model.choices.extend([(x, x) for x in sorted(models)])
        form.model.default = form.model.data
    form.year_from.choices = [('', '')]
    form.year_from.choices.extend([(str(x), str(x)) for x in range(date.today().year, 1899, -1)])
    form.year_from.default = request.args.get('year_from')
    form.year_to.choices = [('', '')]
    form.year_to.choices.extend([(str(x), str(x)) for x in range(date.today().year, 1899, -1)])
    form.year_to.default = request.args.get('year_to')

    if request.method == 'POST' and form.validate():
        # Создание рассылки
        Delivery(user_id=current_user.get_id(),
                 manufacturer=form.manufacturer.data,
                 model=form.model.data,
                 year_from=form.year_from.data,
                 year_to=form.year_to.data,
                 price_from=form.price_from.data.replace(' ', ''),
                 price_to=form.price_to.data.replace(' ', ''),
                 transmission=form.transmission.data
                 ).save()

        # Переадресация с сообщением об успехе
        flash('Рассылка успешно создана. '
              'Скоро вам начнут приходить E-Mail с новыми объявлениями о продаже автомобилей')
        return redirect(url_for('cabinet.deliveries'))

    return render_template("cabinet/deliveries/create.html",
                           form=form)


@cabinet.route('/cabinet/deliveries/toggle-enabled/<delivery_id>/')
@login_required
def toggle_delivery_enabled(delivery_id):
    """Переключает поле enabled на противоположное.

    :param delivery_id: id рассылки
    """
    delivery = Delivery.objects(id=delivery_id, user_id=current_user.get_id()).first_or_404()
    delivery.enabled = not delivery.enabled
    delivery.save()

    flash('Изменения успешно сохранены.')
    return redirect(url_for('cabinet.deliveries'))


@cabinet.route('/cabinet/deliveries/delete/<delivery_id>/', methods=['GET', 'POST'])
@login_required
def delete_delivery(delivery_id):
    """Удаляет рассылку.

    :param delivery_id: id рассылки
    """
    delivery = Delivery.objects(id=delivery_id, user_id=current_user.get_id()).first_or_404()
    delivery.delete()

    flash('Рассылка успешно удалена.')
    return redirect(url_for('cabinet.deliveries'))


@cabinet.route('/cabinet/billing/', methods=['GET', 'POST'])
@login_required
def billing():
    form = BillingForm(request.form, meta={'locales': ['ru_RU', 'ru']})

    if request.method == 'POST' and form.validate():
        # Создание заказа
        order = Order(sum=int(form.sum.data), user=current_user.id).save()

        # Переадресация на Яндекс.Деньги
        form_data = {
            'receiver': form.receiver.data,
            'formcomment': form.formcomment.data,
            'short-dest': form.shortdest.data,
            'quickpay-form': form.quickpayform.data,
            'targets': form.targets.data,
            'paymentType': form.paymentType.data,
            'sum': form.sum.data,
            'successURL': form.successURL.data,
            'label': order.id
        }
        url = 'https://money.yandex.ru/quickpay/confirm.xml?{}'.format(urlencode(form_data))
        return redirect(url, code=307)

    # Заполнение некоторых полей формы дефолтными значениями
    form.receiver.default = current_app.config.get('YANDEX_MONEY_ACCOUNT')
    form.formcomment.default = current_app.config.get('YANDEX_MONEY_FORMCOMMENT')
    form.shortdest.default = current_app.config.get('YANDEX_MONEY_FORMCOMMENT')
    form.successURL.default = url_for('cabinet.billing', _external=True)
    form.process()

    return render_template("cabinet/billing.html", form=form)


@cabinet.route('/cabinet/tariff/', methods=['GET', 'POST'])
@login_required
def tariff():
    form = None
    if datetime.now() < current_user.tariff_expires_at:
        user_tariff = current_user.last_tariff
        if not user_tariff:
            user_tariff = 'Демо'
    else:
        user_tariff = None
        form = TariffForm(request.form, meta={'locales': ['ru_RU', 'ru']})

        choices = [(x.id, x.title +
                    ' (' + str(x.duration) +
                    ' дней, <strong>' +
                    str(x.price) +
                    ' руб.</strong>)')
                   for x in Tariff.objects(enabled=True).order_by('price')]
        if choices:
            form.tariff.choices = choices
        form.tariff.default = request.args.get('tariff', choices[0][0])

        if request.method == 'POST' and form.validate():
            selected_tariff = Tariff.objects(id=form.tariff.data).first()
            current_user.tariff_expires_at = datetime.now() + timedelta(days=selected_tariff.duration)
            current_user.last_tariff = selected_tariff
            current_user.balance -= selected_tariff.price
            current_user.save()
            # Переадресация с сообщением об успехе
            flash('Тариф успешно активирован. Вы можете пользоваться всеми услугами сайта.')
            return redirect(url_for('cabinet.tariff'))

    return render_template("cabinet/tariff.html",
                           user_tariff=user_tariff,
                           form=form)
