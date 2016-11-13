from flask import Blueprint, render_template
from app.models import Page

about = Blueprint('about', __name__)


@about.route('/about/')
def index():
    """Отображает страницу Про сервис"""
    # Данные страницы
    page_data = Page.objects(slug='about').first()

    return render_template("about/index.html",
                           page_data=page_data)
