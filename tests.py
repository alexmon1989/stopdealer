from seeder import clear_db, seed_pages, seed_blog, seed_users
from app import create_app as create_app_base
import unittest
import pymongo
from app.models import User, Search


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app_base(
            MONGODB_DB='testing',
            TESTING=True,
            DEBUG=False,
            DEBUG_TB_INTERCEPT_REDIRECTS=False,
            WTF_CSRF_ENABLED=False
        )
        # Данные для авторизации
        self.email = 'alex.mon1989@gmail.com'
        self.password = '123OLOLO123'
        # Тест-клиент
        self.tester = self.app.test_client(self)
        # Заполнение тестовой БД
        with self.app.app_context():
            clear_db()
            seed_pages()
            seed_blog()
            seed_users()

    def tearDown(self):
        # Удаление тестовой БД
        connection = pymongo.MongoClient()
        connection.drop_database('testing')

    def login(self, email, password):
        return self.tester.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.tester.get('/logout', follow_redirects=True)

    def test_create_app(self):
        assert self.app.config['TESTING']
        assert self.app.config['MONGODB_DB'] == 'testing'

    def test_main_page(self):
        """Тест главной страницы"""
        response = self.tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        # "Главная страница" в title
        self.assertIn("Главная страница", response.data.decode("utf-8"))
        # Зеркало главной
        response = self.tester.get('/home/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Главная страница", response.data.decode("utf-8"))

    def test_main_page_last_searches_widget(self):
        pass

    def test_main_page_cheapened_autos_widget(self):
        pass

    def test_main_page_last_articles_widget(self):
        pass

    def test_main_page_popular_articles_widget(self):
        pass

    def test_main_page_your_searches_widget(self):
        """Тест виджета Ваши поиски"""
        # Пользователь неавторизированный
        response = self.tester.get('/', content_type='html/text')
        self.assertIn("a href=\"/login\">Авторизируйтесь</a>, чтобы увидеть историю ваших поисков",
                      response.data.decode("utf-8"))

        # Авторизация пользователя
        self.login(email=self.email, password=self.password)

        # Вначале поисков нету
        response = self.tester.get('/', content_type='html/text')
        self.assertIn("Вы ещё ничего не искали.", response.data.decode("utf-8"))

        # Добавление в коллекцию БД поисков
        user = User.objects(email=self.email).first()
        Search(phone='1111111',
               user=user.id,
               success=True).save()
        Search(phone='2222222',
               user=user.id,
               success=True).save()
        Search(phone='3333333',
               user=user.id,
               success=False).save()
        response = self.tester.get('/', content_type='html/text')
        self.assertIn("<td>1111111</td>", response.data.decode("utf-8"))
        self.assertIn("<td>2222222</td>", response.data.decode("utf-8"))
        self.assertIn("<td>3333333</td>", response.data.decode("utf-8"))

        # Выход пользователя (logout)
        self.logout()


if __name__ == '__main__':
    unittest.main()
