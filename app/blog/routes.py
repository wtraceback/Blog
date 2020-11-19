from flask import current_app, render_template, request, flash, redirect, url_for
from app.blog import blog_bp
from app.models import Post, Category, Comment
from app.forms import CommentForm, AdminCommentForm
from app import db
from flask_login import current_user


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


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
    # pagination = Comment.query.with_parent(post).filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.username
        form.email.data = current_user.email
        form.site.data = url_for('blog.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(author=author, email=email, site=site, body=body, from_admin=from_admin, post=post)
        replied_id = request.args.get('reply')

        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            # 发邮件通知
        db.session.add(comment)
        db.session.commit()

        if current_user.is_authenticated:
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be publish after reviewed.', 'info')
            # 发邮件通知

        return redirect(url_for('blog.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, form=form, pagination=pagination, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.post.can_comment:
        return redirect(url_for('blog.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + "#comment-form")

    flash('Comment is disabled!', 'warning')
    return redirect(url_for('blog.show_post', post_id=comment.post.id))
