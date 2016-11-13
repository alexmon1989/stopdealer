from flask import Blueprint, render_template, request
from app.models import Automobile, Search
from flask_security import current_user, login_required

phone = Blueprint('phone', __name__)


@phone.route('/info/')
@login_required
def index():
    """Отображет индексную страницу модуля"""
    # Получение номера телефона и приведение его к виду без спец. символов, пробелов и кода +7
    phone_num = request.args.get('phone')\
        .replace('+8', '')\
        .replace('+7', '')\
        .replace('-', '')\
        .replace('(', '')\
        .replace(')', '')\
        .replace(' ', '')
    # Если первая цифра 7 или 8, то убираем её
    if phone_num[0] in ['7', '8']:
        phone_num = phone_num[1:]

    # Поиск по номеру среди автомобилей
    automobiles = Automobile.objects(seller__phone=phone_num).order_by('-created_at')
    automobiles_count = len(automobiles)

    # Среди найденных автомобилей поиск имени владельца (т.к. не во всех объявлениях он есть)
    seller_name = 'нет данных'
    for auto in automobiles:
        if auto.seller['name']:
            seller_name = auto.seller['name']
            break

    # Лог запросов
    Search(phone=phone_num,
           user=current_user.id,
           success=bool(automobiles_count),
           last_automobile=(automobiles[automobiles_count - 1] if automobiles_count > 0 else None)).save()

    # Количество поисков этого номера
    search_count = Search.objects(phone=phone_num).count()

    return render_template("phone/index.html",
                           phone_num=phone_num,
                           search_count=search_count,
                           automobiles=automobiles,
                           automobiles_count=automobiles_count,
                           seller_name=seller_name)
