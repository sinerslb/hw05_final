# posts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Comment, Follow

User = get_user_model()


"""Количество отображаемых постов на главной странице и в группах.
"""
POST_COUNT: int = 10


def pagination(request, post_list):
    """Пагинатор."""
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    """Wiew функция главной страницы."""

    page_obj = pagination(request, Post.objects.all())
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View функция постов выбранной группы."""

    group = get_object_or_404(Group, slug=slug)
    page_obj = pagination(request, group.posts.all())
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профиль пользователя, со всеми его постами."""

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    page_obj = pagination(request, posts)
    following = Follow.objects.filter(
        user=request.user.id, author=author.id).exists()
    its_not_me = request.user.id != author.id
    context = {
        'author': author,
        'page_obj': page_obj,
        'count': count,
        'following': following,
        'its_not_me': its_not_me,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Подробности поста, с комментариями."""
    post = get_object_or_404(Post, id=post_id)
    count_post = Post.objects.filter(author_id=post.author_id).count()
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count': count_post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('posts:profile', username=request.user)

        return render(request, 'posts/create_post.html', {'form': form})

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    context = {'is_edit': True}
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post_id=post.id)

        context['form'] = form

        return render(request, 'posts/create_post.html', context)

    context['form'] = form

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Все посты авторов, на которых подписан пользователь."""
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    if request.user.id != author.id:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    Follow.objects.filter(
        user=request.user,
        author__username=username
    ).delete()

    return redirect('posts:profile', username=username)
