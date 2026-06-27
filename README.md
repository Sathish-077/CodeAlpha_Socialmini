# ✦ SocialMini

A full-stack mini social media platform built with Django + vanilla HTML/CSS/JS.

## Features

- **User Accounts** — Register, login, logout with persistent sessions
- **Profiles** — Customizable avatar color, bio, website; followers/following counts
- **Posts** — Create & delete posts (up to 500 chars) with a real-time character counter
- **Comments** — Add & delete comments inline without page reload (AJAX)
- **Likes** — Toggle likes on any post with instant UI feedback (AJAX)
- **Follow System** — Follow/unfollow users; personalized feed shows followed users' posts
- **Explore** — Browse all posts across the platform
- **Search** — Find users by name/username and posts by content
- **Suggested Users** — Sidebar recommendations of people to follow
- **Django Admin** — Full admin panel at `/admin/`

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Django 4.x |
| Database | SQLite (dev), easily swappable to PostgreSQL |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Auth | Django built-in auth |
| Async interactions | Fetch API (no page reloads for likes, comments, follows) |

## Project Structure

```
socialmini/
├── manage.py
├── setup_and_run.sh          # One-command setup + seed + run
├── db.sqlite3                # Created on first run
├── socialmini/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/                     # Main app
    ├── models.py             # Profile, Post, Comment, Like, Follow
    ├── views.py              # All views (feed, profile, search, AJAX endpoints)
    ├── urls.py               # URL routing
    ├── forms.py              # Django forms
    ├── admin.py              # Admin registration
    ├── signals.py            # Auto-create Profile on User creation
    ├── templates/core/
    │   ├── base.html         # Navigation, layout shell
    │   ├── login.html
    │   ├── register.html
    │   ├── feed.html         # Main home feed
    │   ├── explore.html      # All posts
    │   ├── profile.html      # User profile with tabs
    │   ├── edit_profile.html
    │   ├── post_detail.html  # Single post + all comments
    │   ├── search.html
    │   └── _post_card.html   # Reusable post partial
    └── static/core/
        ├── css/main.css      # Full design system (dark theme)
        └── js/app.js         # AJAX for likes, follows, comments
```

## Database Models

```
User (Django built-in)
 └── Profile          (1:1) — bio, avatar_color, website
 └── Post             (1:N) — content, created_at
     └── Comment      (1:N) — content, author
     └── Like         (M:N) — unique(user, post)
 └── Follow           (M:N) — unique(follower, following)
```

## Quick Start

### Requirements
- Python 3.10+
- pip

### Run (one command)

```bash
cd socialmini
chmod +x setup_and_run.sh
./setup_and_run.sh
```

Then open http://127.0.0.1:8000

### Manual setup

```bash
pip install django
cd socialmini
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Demo Accounts

After running `setup_and_run.sh`:

| Username | Password |
|---|---|
| alice | pass123 |
| bob | pass123 |
| carol | pass123 |
| dave | pass123 |
| eve | pass123 |
| admin | admin123 |

## API Endpoints (AJAX)

| Method | URL | Description |
|---|---|---|
| POST | `/post/<id>/like/` | Toggle like → `{liked, count}` |
| POST | `/post/<id>/comment/` | Add comment → `{success, id, content, …}` |
| POST | `/comment/<id>/delete/` | Delete comment → `{success}` |
| POST | `/follow/<username>/` | Toggle follow → `{following, followers_count}` |

## Production Notes

- Change `SECRET_KEY` in settings.py
- Set `DEBUG = False`
- Use PostgreSQL: `pip install psycopg2-binary` and update `DATABASES`
- Run `python manage.py collectstatic`
- Use gunicorn + nginx for serving
