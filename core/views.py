from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from django.contrib import messages
import json

from .models import Profile, Post, Comment, Like, Follow
from .forms import RegisterForm, LoginForm, PostForm, CommentForm, ProfileEditForm


def get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


# ── Auth Views ──────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile is auto-created by signal in signals.py
            login(request, user)
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            get_or_create_profile(user)
            return redirect('feed')
        else:
            error = 'Invalid username or password.'
    return render(request, 'core/login.html', {'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ── Feed ────────────────────────────────────────────────────────────────────

@login_required
def feed_view(request):
    get_or_create_profile(request.user)
    # Posts from people the user follows + own posts
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_ids) | Q(author=request.user)
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments')

    # Suggested users: not yet following, not self
    suggested = User.objects.exclude(id=request.user.id).exclude(id__in=following_ids).order_by('?')[:5]

    liked_post_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, 'core/feed.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids,
        'suggested': suggested,
        'post_form': PostForm(),
    })


# ── Posts ────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
    return redirect('feed')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return redirect('feed')


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author', 'author__profile')
    liked = Like.objects.filter(user=request.user, post=post).exists()
    is_following = Follow.objects.filter(follower=request.user, following=post.author).exists()
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
        'liked': liked,
        'comment_form': CommentForm(),
        'is_following': is_following,
    })


# ── Comments ─────────────────────────────────────────────────────────────────

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    if content:
        comment = Comment.objects.create(post=post, author=request.user, content=content)
        profile = get_or_create_profile(request.user)
        return JsonResponse({
            'success': True,
            'id': comment.id,
            'content': comment.content,
            'author': request.user.username,
            'avatar_color': profile.avatar_color,
            'created_at': comment.created_at.strftime('%b %d, %Y'),
            'count': post.comments.count(),
        })
    return JsonResponse({'success': False}, status=400)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post_id = comment.post_id
    comment.delete()
    return JsonResponse({'success': True})


# ── Likes ─────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})


# ── Follow ───────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
    return JsonResponse({
        'following': following,
        'followers_count': Follow.objects.filter(following=target).count(),
    })


# ── Profiles ─────────────────────────────────────────────────────────────────

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_or_create_profile(user)
    posts = Post.objects.filter(author=user).select_related('author__profile')
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    liked_post_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    followers = Follow.objects.filter(following=user).select_related('follower', 'follower__profile')
    following = Follow.objects.filter(follower=user).select_related('following', 'following__profile')

    return render(request, 'core/profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'liked_post_ids': liked_post_ids,
        'followers': followers,
        'following_list': following,
    })


@login_required
def edit_profile(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    return render(request, 'core/edit_profile.html', {'form': form, 'profile': profile})


# ── Search ───────────────────────────────────────────────────────────────────

@login_required
def search_view(request):
    q = request.GET.get('q', '').strip()
    users = []
    posts = []
    if q:
        users = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).exclude(id=request.user.id)[:10]
        posts = Post.objects.filter(content__icontains=q).select_related('author', 'author__profile')[:20]
    following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    liked_post_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    return render(request, 'core/search.html', {
        'q': q,
        'users': users,
        'posts': posts,
        'following_ids': following_ids,
        'liked_post_ids': liked_post_ids,
    })


# ── Explore ──────────────────────────────────────────────────────────────────

@login_required
def explore_view(request):
    posts = Post.objects.all().select_related('author', 'author__profile').prefetch_related('likes', 'comments').order_by('-created_at')[:50]
    liked_post_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    return render(request, 'core/explore.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids,
    })
