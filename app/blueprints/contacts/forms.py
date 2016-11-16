from wtforms import Form, TextAreaField, StringField, validators


class ContactsForm(Form):
    """Класс формы контактов"""
    username = StringField('Ваше имя', [validators.Length(min=3, max=60)])
    email = StringField('Ваш Email', [validators.Email()])
    telephone = StringField('Ваш телефон')
    message = TextAreaField('Сообщение', [validators.Length(min=10)])
