# coding: utf-8
from app.models import Page, Blog, User
from app import create_app, user_datastore
from flask_security.utils import encrypt_password


# Очистка коллекций БД
def clear_db():
    Page.objects.delete()
    Blog.objects.delete()
    User.objects.delete()


# Заполнение коллекции pages
def seed_pages():
    Page(
        slug='home',
        title="Определение \"перекупщика\" по номеру телефона - Главная страница",
        content="<p>Наш сервис предоставляет услугу по получению информации о владельце авто по номеру телефона.</p><p>Известный факт, что б/у автомобили, которые продают \"перекупщики\", часто оказываются в плохом состоянии. Как правило производится дешёвый ремонт и авто попадает на автобазар, где эти люди уверяют вас, что авто \"не бито, не крашено\".</p><p>Мы долгое время собираем для вас информацию о номерах телефонов автопродавцов и вы сможете узнать сколько автомобилей продавалось по конкретному номеру телефона. Данная информация поможет вам определить перекупщика: если по этому номеру продавалась одна машина год назад, то вероятность, что это перекупщик низкая, а если 50 авто за последний год, то здесь всё очевидно!</p><p>Помимо этого мы предлагаем и другие услуги для людей, которые выбирают себе б/у автомобиль. Подробнее вы можете узнать об этом <a href=\"#\">здесь</a>.</p>",
        head_title="Определение \"перекупщика\" по номеру телефона"
    ).save()
    Page(
        slug='blog',
        title="Блог",
        head_title="Статьи"
    ).save()
    Page(
        slug='about',
        title="Про сервис",
        content="<p>Наш сервис предоставляет услугу по получению информации о владельце авто по номеру телефона.</p><p>Известный факт, что б/у автомобили, которые продают \"перекупщики\", часто оказываются в плохом состоянии. Как правило производится дешёвый ремонт и авто попадает на автобазар, где эти люди уверяют вас, что авто \"не бито, не крашено\".</p><p>Мы долгое время собираем для вас информацию о номерах телефонов автопродавцов и вы сможете узнать сколько автомобилей продавалось по конкретному номеру телефона. Данная информация поможет вам определить перекупщика: если по этому номеру продавалась одна машина год назад, то вероятность, что это перекупщик низкая, а если 50 авто за последний год, то здесь всё очевидно!</p><p>Помимо этого мы предлагаем и другие услуги для людей, которые выбирают себе б/у автомобиль. Подробнее вы можете узнать об этом <a href=\"#\">здесь</a>.</p>",
        head_title="Про сервис"
    ).save()
    Page(
        slug='contacts',
        title="Техническая поддержка и сотрудничество",
        content="<p>Мы с удовольствием ответим на все ваши вопросы и предложения. Данные для контакта вы можете найти на этой странице немного ниже, а также у вас есть возможность отправить нам письмо прямо с сайта через форму связи.</p>",
        head_title="Контакты"
    ).save()
    Page(
        slug='prices',
        title="Стоимость",
        content="<p>Детальная стоимость будет расписана позже.</p>",
        head_title="Цены"
    ).save()


# Заполнение коллекции blog
def seed_blog():
    for i in range(100):
        Blog(
            slug='chem-grozit-pokupka-avto-u-perekupschikov-' + str(i),
            title="Чем грозит покупка авто у \"перекупщиков\"?",
            content="<p>Наш сервис предоставляет услугу по получению информации о владельце авто по номеру телефона.</p><p>Известный факт, что б/у автомобили, которые продают \"перекупщики\", часто оказываются в плохом состоянии. Как правило производится дешёвый ремонт и авто попадает на автобазар, где эти люди уверяют вас, что авто \"не бито, не крашено\".</p><p>Мы долгое время собираем для вас информацию о номерах телефонов автопродавцов и вы сможете узнать сколько автомобилей продавалось по конкретному номеру телефона. Данная информация поможет вам определить перекупщика: если по этому номеру продавалась одна машина год назад, то вероятность, что это перекупщик низкая, а если 50 авто за последний год, то здесь всё очевидно!</p><p>Помимо этого мы предлагаем и другие услуги для людей, которые выбирают себе б/у автомобиль. Подробнее вы можете узнать об этом <a href=\"#\">здесь</a>.</p>",
            head_title="Чем грозит покупка авто у \"перекупщиков\"?"
        ).save()


# Заполнение коллекции users
def seed_users():
    user_datastore.find_or_create_role(name='admin', description='Администратор')
    user_datastore.find_or_create_role(name='user', description='Пользователь')
    user_datastore.create_user(
        email='alex.mon1989@gmail.com',
        username='Монастырецкий Александр Николаевич',
        password=encrypt_password('123OLOLO123')
    )
    user_datastore.add_role_to_user('alex.mon1989@gmail.com', 'admin')
    user_datastore.add_role_to_user('alex.mon1989@gmail.com', 'user')


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print('Очистка коллекций...')
        clear_db()
        print('Заполнение коллекции pages...')
        seed_pages()
        print('Заполнение коллекции blog...')
        seed_blog()
        print('Заполнение коллекции users...')
        seed_users()
