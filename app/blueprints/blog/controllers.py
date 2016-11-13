from flask import Blueprint, render_template
from app.models import Blog, Page

blog = Blueprint('blog', __name__)


@blog.route('/blog/', defaults={'page': 1})
@blog.route('/blog/page/<int:page>/')
def index(page=1):
    """Отображает страницу со списком статей."""
    # Данные страницы
    page_data = Page.objects(slug='blog').first()

    articles = Blog.objects.paginate(page=page, per_page=5)

    return render_template("blog/index.html",
                           page_data=page_data,
                           articles=articles)


@blog.route('/blog/<slug>')
def show(slug):
    """Отображает страницу со статьёй <slug>"""
    article = Blog.objects.get_or_404(slug=slug)
    article.visits += 1
    article.save()

    return render_template("blog/show.html",
                           article=article)
