from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

from django.contrib.auth.decorators import login_required


User = get_user_model()

POSTS_COUNT = 10


def pagination(request, queryset):
    paginator = Paginator(queryset, POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    queryset = Post.objects.all()
    page_obj = pagination(request=request, queryset=queryset)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug=None):
    """View-функция для страницы сообщества"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    page_obj = pagination(request, posts)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'count': count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    all_posts = author.posts.all()
    count = all_posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'count': count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
        'is_edit': False,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post.id)
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post.id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # Получите пост
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """список постов избранных авторов"""
    queryset = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request=request, queryset=queryset)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    user = request.user
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка"""
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    is_follower.delete()
    return redirect('posts:profile', username=author)
