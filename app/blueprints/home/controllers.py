from flask import Blueprint, render_template
from app.models import Automobile, Page, Blog, Price, Search, CheapenedAuto
from flask_security import current_user

home = Blueprint('home', __name__)


@home.route('/')
@home.route('/home/')
def index():
    """Отображает главную страницу"""
    # Данные страницы
    page_data = Page.objects(slug='home').first()

    # Подешевевшие автомобили
    cheapened_autos = CheapenedAuto.objects.order_by('-created_at')[:10]

    # Популярные статьи
    popular_articles = Blog.objects(enabled=True).order_by('-visits')[:5]

    # Последние статьи
    last_articles = Blog.objects(enabled=True).order_by('-created_at')[:5]

    # Данные для виджета counter
    auto_count = Automobile.objects.count()
    sellers_count = Automobile.get_seller_phones_count()

    # Последние поиски:
    last_searches = Search.objects(success=True).order_by('-created_at')[:5]

    # Последние поиски залогиненного пользователя
    last_searches_user = []
    if current_user.is_authenticated:
        last_searches_user = Search.objects(user=current_user.id).order_by('-created_at')[:10]

    return render_template("home/index.html",
                           page_data=page_data,
                           popular_articles=popular_articles,
                           last_articles=last_articles,
                           auto_count=auto_count,
                           sellers_count=sellers_count,
                           cheapened_autos=cheapened_autos,
                           last_searches=last_searches,
                           last_searches_user=last_searches_user)
