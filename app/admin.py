from .models import User, Blog, Page, Search, Delivery, Order, Tariff, Settings
from wtforms import TextAreaField, PasswordField, validators
from wtforms.widgets import TextArea
from flask import url_for, redirect, request, abort
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.base import MenuLink
from flask_admin.contrib.mongoengine import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_security import current_user
from flask_security.utils import encrypt_password
from flask_wtf import FlaskForm
from slugify import slugify
import datetime
import os.path as op
from flask_admin.contrib.mongoengine.filters import BaseMongoEngineFilter


# CKEditor
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


# Переопределение класса для обеспечения интеграции с Flask-Security
class MyModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Переопределение класса для обеспечения интеграции с Flask-Security
class MyFileAdmin(FileAdmin):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Главная страница
class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# ModelView для администрирования пользователей
class AdminUserModelView(MyModelView):
    list_template = 'admin/user/custom_list.html'
    details_template = 'admin/user/custom_details.html'
    edit_template = 'admin/user/custom_edit.html'
    can_view_details = True
    form_base_class = FlaskForm
    column_details_exclude_list = ('password', 'confirmed_at')
    column_exclude_list = ('password',
                           'confirmed_at',
                           'current_login_ip',
                           'login_count',
                           'last_login_ip',
                           'current_login_at',
                           'last_login_at',
                           'tariff_expires_at',
                           'deliveries_count',
                           'last_tariff')
    column_labels = dict(email='E-Mail',
                         username='Имя пользователя',
                         balance='Баланс, руб.',
                         active='Профиль включён?',
                         roles='Роли',
                         last_login_at='Последняя авторизация',
                         current_login_at='Текущая авторизация',
                         current_login_ip='IP при текущей авторизации',
                         last_login_ip='IP при последней авторизации',
                         login_count='Заходил, раз',
                         last_tariff='Тариф',
                         tariff_expires_at='Время истечения срока тарифа',
                         deliveries_count='Количество купленных подписок',
                         created_at='Создано',
                         updated_at='Последнее редактирование')
    column_formatters = dict(current_login_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'),
                             tariff_expires_at=lambda v, c, m, p: m.tariff_expires_at.strftime('%d.%m.%Y %H:%M:%S'),
                             created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             updated_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'))
    form_excluded_columns = ('created_at',
                             'updated_at',
                             'confirmed_at',
                             'current_login_ip',
                             'last_login_ip',
                             'current_login_at',
                             'last_login_at',
                             'login_count')
    column_default_sort = ('created_at', True)
    column_editable_list = ('active', )
    column_searchable_list = ('email', 'username')
    column_filters = ('active',)
    form_args = {
        'email': {
            'label': 'E-Mail',
            'validators': [validators.email()]
        },
        'username': {
            'label': 'Имя пользователя',
            'validators': [validators.required()]
        },
        'balance': {
            'label': 'Баланс, руб',
            'validators': [validators.NumberRange(min=0.00)]
        },
        'active': {
            'label': 'Профиль включён',
        },
        'last_tariff': {
            'label': 'Тариф',
        },
        'tariff_expires_at': {
            'label': 'Время истечения срока тарифа',
        },
        'deliveries_count': {
            'label': 'Количество купленных подписок',
        }
    }
    form_widget_args = {
        'password': {
            'placeholder': 'В случае редактирования оставьте пустым, если не хотите менять'
        }
    }
    form_extra_fields = {
        'password': PasswordField('Пароль', [validators.Optional(), validators.Length(min=6)])
    }

    def on_model_change(self, form, model, is_created):
        model.updated_at = datetime.datetime.now
        if form.password.data != '':
            model.password = encrypt_password(form.password.data)
        else:
            model.password = User.objects(id=model.id).only('password').first()['password']

    @expose('/search_queries/')
    def search_queries_view(self):
        """Действие для отображения страницы с поисковыми запросами пользователя."""
        search_queries = Search.objects(user=request.args.get('id')).order_by('-created_at')

        return self.render('admin/user/search_queries.html',
                           search_queries=search_queries,
                           search_queries_count=len(search_queries),
                           return_url=request.args.get('url'))


# ModelView для администрирования блога
class AdminBlogModelView(MyModelView):
    form_base_class = FlaskForm
    form_overrides = {
        'content': CKTextAreaField
    }
    create_template = 'create.html'
    edit_template = 'edit.html'
    can_view_details = True
    column_details_exclude_list = ('content',)
    column_exclude_list = ('content', 'head_title', 'meta_description', 'meta_keywords', 'slug')
    form_excluded_columns = ('created_at', 'updated_at')
    column_labels = dict(title='Название',
                         visits='Просмотров',
                         enabled='Включено',
                         created_at='Создано',
                         updated_at='Последнее редактирование')
    column_formatters = dict(created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             updated_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'))
    form_args = {
        'title': {
            'label': 'Название',
            'validators': [validators.required()]
        },
        'content': {
            'label': 'Содержание',
            'validators': [validators.required()]
        },
        'visits': {
            'label': 'Просмотров',
            'validators': [validators.NumberRange(min=0)]
        },
        'head_title': {
            'label': 'Title страницы',
        },
        'meta_description': {
            'label': 'Description страницы',
        },
        'meta_keywords': {
            'label': 'Ключевые слова (keywords)',
        },
        'enabled': {
            'label': 'Включено',
        }
    }
    column_editable_list = ('enabled',)
    column_searchable_list = ('title',)
    column_default_sort = ('created_at', True)
    form_widget_args = {
        'slug': {
            'placeholder': 'Создастся автоматически или введите сами'
        },
        'head_title': {
            'placeholder': 'Создастся автоматически или введите сами'
        }
    }

    def on_model_change(self, form, model, is_created):
        if not form.slug.data:
            model.slug = slugify(form.title.data)
        # Проверка slug на уникальность
        i = 1
        if is_created:
            while Blog.objects(slug=model.slug).count() > 0:
                model.slug = model.slug + '-' + str(i)
                i += 1
        else:
            while Blog.objects(id__ne=model.id, slug=model.slug).count() > 0:
                model.slug = model.slug + '-' + str(i)
                i += 1
        if not form.head_title.data:
            model.head_title = form.title.data
        model.updated_at = datetime.datetime.now


# ModelView для администрирования страниц сайта
class AdminPagesModelView(MyModelView):
    form_base_class = FlaskForm
    form_overrides = {
        'content': CKTextAreaField,
        'contact_widget_content': CKTextAreaField
    }
    create_template = 'create.html'
    edit_template = 'edit.html'
    can_create = False
    can_delete = False
    column_exclude_list = ('content',
                           'head_title',
                           'meta_description',
                           'meta_keywords',
                           'contact_form_email',
                           'contact_widget_content')
    form_excluded_columns = ('created_at', 'updated_at')
    column_labels = dict(title='Название',
                         content='Содержание',
                         head_title='Title страницы',
                         created_at='Создано',
                         updated_at='Последнее редактирование')
    column_formatters = dict(created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             updated_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'))
    form_args = {
        'title': {
            'label': 'Название',
            'validators': [validators.required()]
        },
        'content': {
            'label': 'Содержание',
            'validators': [validators.required()]
        },
        'head_title': {
            'label': 'Title страницы',
        },
        'meta_description': {
            'label': 'Description страницы',
        },
        'contact_form_email': {
            'label': 'E-Mail, на который отправляется форма',
            'validators': [validators.email()]
        },
        'contact_widget_content': {
            'label': 'Текст виджета "Контакты"',
        }
    }
    form_widget_args = {
        'slug': {
            'disabled': 'disabled'
        }
    }

    def on_model_change(self, form, model, is_created):
        model.slug = Page.objects(id=model.id).only('slug').first()['slug']
        model.updated_at = datetime.datetime.now

    def on_form_prefill(self, form, id):
        page = Page.objects(id=id).first()
        if page.slug != 'contacts':
            del form.contact_form_email
            del form.contact_widget_content


class FilterUserId(BaseMongoEngineFilter):
    """Кастомный фильтр для поиска по E-Mail пользователей."""
    def apply(self, query, value, alias=None):
        user_ids = [user.id for user in User.objects(email=value)]
        return query.filter(user_id__in=user_ids)

    def operation(self):
        return 'Равно'


class AdminDeliveriesModelView(MyModelView):
    """ModelView Для администрирования подписок"""
    form_base_class = FlaskForm
    create_template = 'create.html'
    edit_template = 'edit.html'
    can_view_details = True
    can_create = False
    can_edit = False
    can_delete = True
    column_exclude_list = ('updated_at', )
    column_labels = dict(user_id='Пользователь',
                         manufacturer='Производитель',
                         model='Модель',
                         year_from='Год от',
                         year_to='Год до',
                         price_from='Цена от',
                         price_to='Цена до',
                         transmission='КПП',
                         enabled='Вкл.',
                         created_at='Создано',
                         expires_at='Истекает',
                         last_letter_at='Последнее письмо')
    column_formatters = dict(user_id=lambda v, c, m, p: m.user_id.email,
                             created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             updated_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'),
                             expires_at=lambda v, c, m, p: m.expires_at.strftime('%d.%m.%Y %H:%M:%S'),
                             last_letter_at=lambda v, c, m, p: m.last_letter_at.strftime('%d.%m.%Y %H:%M:%S'))
    column_editable_list = ('enabled',)
    column_filters = (FilterUserId(column=Delivery.user_id, name='Пользователь (E-Mail)'),
                      'enabled',
                      'manufacturer',
                      'model')


class FilterUser(BaseMongoEngineFilter):
    """Кастомный фильтр для поиска по E-Mail пользователей."""
    def apply(self, query, value, alias=None):
        user_ids = [user.id for user in User.objects(email=value)]
        return query.filter(user__in=user_ids)

    def operation(self):
        return 'Равно'


class AdminOrdersModelView(MyModelView):
    """ModelView для администрирования оплат"""
    form_base_class = FlaskForm
    can_view_details = True
    can_delete = True
    can_edit = False
    can_create = False
    column_labels = dict(user='Пользователь',
                         sum='Сумма',
                         created_at='Создано',
                         paid_at='Оплачено')
    column_formatters = dict(user=lambda v, c, m, p: m.user.email,
                             created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             paid_at=lambda v, c, m, p: m.paid_at.strftime('%d.%m.%Y %H:%M:%S'))
    column_filters = (FilterUser(column=Order.user, name='Пользователь (E-Mail)'), 'sum', 'paid_at', 'created_at')

    def get_query(self):
        """Фильтр по умолчанию: отображаются только оплаченные заказы."""
        return self.model.objects(paid_at__ne=None)


class AdminTariffModelView(MyModelView):
    """ModelView для администрирования тарифов"""
    form_base_class = FlaskForm
    can_view_details = True
    can_delete = False
    can_edit = True
    can_create = True
    column_labels = dict(title='Название',
                         price='Стоимость, руб.',
                         duration='Продолжительность, дней',
                         enabled='Активирован?',
                         created_at='Создано',
                         updated_at='Последнее редактирование')
    column_editable_list = ('enabled',)
    form_args = {
        'title': {
            'label': 'Название',
            'validators': [validators.required()]
        },
        'price': {
            'label': 'Стоимость, руб.',
            'validators': [validators.required()]
        },
        'duration': {
            'label': 'Продолжительность действия, дней',
            'validators': [validators.required()]
        },
        'enabled': {
            'label': 'Активирован? (отображается ли в списке выбора)',
        }
    }
    form_excluded_columns = ('created_at', 'updated_at')
    column_formatters = dict(created_at=lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                             updated_at=lambda v, c, m, p: m.updated_at.strftime('%d.%m.%Y %H:%M:%S'))
    column_filters = ('title', 'enabled', 'price', 'duration', 'created_at', 'updated_at')

    def on_model_change(self, form, model, is_created):
        model.updated_at = datetime.datetime.now


class AdminSettingsModelView(MyModelView):
    """ModelView для администрирования тарифов"""
    form_base_class = FlaskForm
    can_delete = False
    can_edit = True
    can_create = False
    column_labels = dict(title='Название настройки',
                         value='Значение')
    form_args = {
        'value': {
            'label': 'Значение',
            'validators': [validators.required()]
        },
    }
    form_excluded_columns = ('title', 'key')
    column_exclude_list = ('key',)
    column_formatters = dict(
        value=lambda v, c, m, p: m.value.replace('True', 'Да').replace('False', 'Нет')
        if m.value in ('True', 'False')
        else m.value
    )


# Инициализация админ. панели
admin = Admin(name='Stopdealer',
              template_mode='bootstrap3',
              index_view=MyHomeView(menu_icon_type='glyph', menu_icon_value='glyphicon-home'))
admin.add_view(AdminPagesModelView(Page,
                                   name='Страницы',
                                   endpoint='pages_admin',
                                   url='pages',
                                   menu_icon_type='glyph',
                                   menu_icon_value='glyphicon-list'))
admin.add_view(AdminBlogModelView(Blog,
                                  name='Блог',
                                  endpoint='blog_admin',
                                  url='blog',
                                  menu_icon_type='glyph',
                                  menu_icon_value='glyphicon-book'))
admin.add_view(AdminDeliveriesModelView(Delivery,
                                        name='Подписки',
                                        menu_icon_type='glyph',
                                        menu_icon_value='glyphicon-tasks'))
admin.add_view(AdminTariffModelView(Tariff,
                                    name='Тарифы',
                                    menu_icon_type='glyph',
                                    menu_icon_value='glyphicon-flash'))
admin.add_view(AdminOrdersModelView(Order,
                                    name='Оплаты',
                                    menu_icon_type='glyph',
                                    menu_icon_value='glyphicon-ruble'))
admin.add_view(AdminUserModelView(User,
                                  name='Пользователи',
                                  menu_icon_type='glyph',
                                  menu_icon_value='glyphicon-user'))
admin.add_view(AdminSettingsModelView(Settings,
                                      name='Настройки',
                                      menu_icon_type='glyph',
                                      menu_icon_value='glyphicon-cog'))
path = op.join(op.dirname(__file__), 'static', 'uploads')
admin.add_view(FileAdmin(path,
                         '/static/uploads/',
                         name='Загрузки',
                         menu_icon_type='glyph',
                         menu_icon_value='glyphicon-picture'))
admin.add_link(MenuLink(name='На сайт',
                        url='/',
                        icon_type='glyph',
                        icon_value='glyphicon-new-window',
                        target='_blank'))


