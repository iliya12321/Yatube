from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .utils import get_page_paginator
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


WORD_LIMIT = 30  # Количество выводимых букв в заголовке профайла


@cache_page(60 * 20)
def index(request):
    """Главная страница"""
    posts = Post.objects.select_related('group', 'author')
    page_obj = get_page_paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Все посты выбранной группы"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_paginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профайл автора"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    post_count = author.posts.all().count()
    title = f'Профайл пользователя {author}'
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    page_obj = get_page_paginator(posts, request)
    context = {
        'following': following,
        'author': author,
        'post_count': post_count,
        'title': title,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Подробная информация выбранного поста"""
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)

    title = f'Пост {post.text[:WORD_LIMIT]}'
    context = {
        'form': form,
        'comments': comments,
        'post_count': post_count,
        'post': post,
        'title': title
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Cтраницa создания новой записи."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    """Страница изменения выбранного поста"""
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    is_edit = True

    if form.is_valid():
        form = form.save(commit=False)
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)

    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit,
        'post_id': post.pk
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Страница добавления комментов"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    page_obj = get_page_paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    follower = Follow.objects.filter(user=user, author=author)
    if user != author and not follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=username)
