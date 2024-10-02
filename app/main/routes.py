from datetime import datetime, timezone

import sqlalchemy as sa
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import Post, User


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    return render_template(
        "index.html",
        title="Home",
        form=form,
        pagination=pagination,
        posts=posts,
    )


@bp.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    pagination = db.paginate(
        query, page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template(
        "index.html",
        title="Explore",
        pagination=pagination,
        posts=posts,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get("page", 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    pagination = db.paginate(
        query, page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    form = EmptyForm()
    return render_template(
        "user.html",
        title="Profile",
        user=user,
        pagination=pagination,
        posts=posts,
        form=form,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.", "danger")
            return redirect(url_for("main.index"))
        if user == current_user:
            flash("You cannot follow yourself!", "warning")
            return redirect(url_for("main.user", username=username))
        current_user.follow(user)
        db.session.commit()
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))


@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.", "danger")
            return redirect(url_for("main.index"))
        if user == current_user:
            flash("You cannot unfollow yourself!", "warning")
            return redirect(url_for("main.user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.index"))
