from flask import current_app, render_template, request
from app.blog import blog_bp
from app.models import Post, Category


@blog_bp.route('/')
@blog_bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page, False)
    posts = pagination.items
    return render_template('blog/index.html', title='Personal-Blog', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    # with_parent(instance)传入模型类实例作为参数，返回和这个实例相关联的对象
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page, False)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)
