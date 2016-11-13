from flask import Blueprint, render_template
from app.models import Page

prices = Blueprint('prices', __name__)


@prices.route('/prices/')
def index():
    """Отображает страницу Про сервис"""
    # Данные страницы
    page_data = Page.objects(slug='prices').first()

    return render_template("prices/index.html",
                           page_data=page_data)
