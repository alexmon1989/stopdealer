from flask import Blueprint, render_template
from app.models import Automobile, Price
from flask_security import login_required

automobile = Blueprint('automobile', __name__)


@automobile.route('/automobile/<auto_id>/')
@login_required
def index(auto_id):
    """Отображает индексную страницу модуля"""
    auto = Automobile.objects(id=auto_id).first_or_404()
    prices = Price.objects(automobile=auto_id)

    return render_template("automobile/index.html",
                           auto=auto,
                           prices=prices)
