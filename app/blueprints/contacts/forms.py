from wtforms import Form, TextAreaField, StringField, validators


class ContactsForm(Form):
    """Класс формы контактов"""
    username = StringField('Имя', [validators.Length(min=3, max=60)])
    email = StringField('Email', [validators.Email()])
    telephone = StringField('Телефон')
    message = TextAreaField('Сообщение', [validators.Length(min=10)])
