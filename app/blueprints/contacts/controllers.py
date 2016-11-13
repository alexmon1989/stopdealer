from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Page
from app.blueprints.contacts.forms import ContactsForm
from flask_mail import Message
from app import mail

contacts = Blueprint('contacts', __name__)


@contacts.route('/contacts/', methods=['GET', 'POST'])
def index():
    """Отображает страницу "Про сервис"""
    form = ContactsForm(request.form, meta={'locales': ['ru_RU', 'ru']})

    # Отправка сообщения с сайта
    if request.method == 'POST' and form.validate():
        msg = Message("Сообщение с сайта",
                      recipients=["to@example.com"])
        msg.html = '''
            <strong>Имя:</strong> {0} <br />
            <strong>E-Mail:</strong> <a href="mailto:{1}">{1}</a>  <br />
            <strong>Телефон:</strong> {2} <br />
            <strong>Сообщение:</strong> {3}
        '''.format(form.username.data, form.email.data, form.telephone.data, form.message.data)
        mail.send(msg)
        flash('Сообщение успешно отправлено. Наши менеджеры свяжутся с вами в ближайшее время.')
        return redirect(url_for('contacts.index'))

    # Данные страницы
    page_data = Page.objects(slug='contacts').first()

    return render_template("contacts/index.html",
                           page_data=page_data,
                           form=form)
