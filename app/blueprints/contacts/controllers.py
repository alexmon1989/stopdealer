from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask import current_app
from app.models import Page
from app.blueprints.contacts.forms import ContactsForm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

contacts = Blueprint('contacts', __name__)


@contacts.route('/contacts/', methods=['GET', 'POST'])
def index():
    """Отображает страницу Контакты"""
    form = ContactsForm(request.form, meta={'locales': ['ru_RU', 'ru']})

    # Данные страницы
    page_data = Page.objects(slug='contacts').first()

    # Отправка сообщения с сайта
    if request.method == 'POST' and form.validate():
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Сообщение пользователя с сайта stopdealer.ru'
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = page_data.contact_form_email
        html = '''
            <strong>Имя:</strong> {0} <br />
            <strong>E-Mail:</strong> <a href="mailto:{1}">{1}</a>  <br />
            <strong>Телефон:</strong> {2} <br />
            <strong>Сообщение:</strong> {3}
        '''.format(form.username.data, form.email.data, form.telephone.data, form.message.data)
        msg.attach(MIMEText(html, 'html'))
        s = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        s.send_message(msg)
        s.quit()
        flash('Сообщение успешно отправлено. Наши менеджеры свяжутся с вами в ближайшее время.')
        return redirect(url_for('contacts.index'))

    return render_template("contacts/index.html",
                           page_data=page_data,
                           form=form)
