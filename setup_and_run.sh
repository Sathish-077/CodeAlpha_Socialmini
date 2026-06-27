#!/usr/bin/env bash
# SocialMini — setup & run script
set -e

echo "🔧 Installing dependencies..."
pip install django

echo "🗄️  Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "👤 Creating superuser (admin / admin123)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

echo "🌱 Seeding demo data..."
python manage.py shell -c "
import random
from django.contrib.auth.models import User
from core.models import Profile, Post, Follow, Like, Comment

colors = ['#6366f1','#ec4899','#10b981','#f59e0b','#3b82f6','#8b5cf6','#06b6d4','#f97316']
usernames = ['alice', 'bob', 'carol', 'dave', 'eve']
bios = [
    'Coffee lover ☕ | Always exploring 🌍',
    'Developer by day, dreamer by night 🌙',
    'Photographer & traveler 📷',
    'Building cool things on the internet 🚀',
    'Reading, writing, repeating ✍️',
]
sample_posts = [
    'Just deployed my first side project! 🎉 Feels amazing to ship something real.',
    'Hot take: the best code is the code you delete.',
    'Spent the morning hiking. Nature is the best reset. 🌿',
    'Read 3 books this month. Highly recommend making time for it.',
    'The secret to productivity? Stop optimizing and start doing.',
    'Anyone else think coffee tastes better when you make it yourself?',
    'Shipped a new feature today. Small wins count!',
    'Learning something new every single day. That\\'s the goal.',
]

for i, uname in enumerate(usernames):
    user, created = User.objects.get_or_create(username=uname)
    if created:
        user.set_password('pass123')
        user.first_name = uname.capitalize()
        user.save()
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.avatar_color = colors[i % len(colors)]
    profile.bio = bios[i]
    profile.save()

all_users = list(User.objects.filter(username__in=usernames))
for post_content in sample_posts:
    author = random.choice(all_users)
    Post.objects.get_or_create(author=author, content=post_content)

# Create some follows
for u in all_users:
    targets = random.sample([x for x in all_users if x != u], k=random.randint(1,3))
    for t in targets:
        Follow.objects.get_or_create(follower=u, following=t)

# Create some likes and comments
posts = list(Post.objects.all())
for post in posts:
    likers = random.sample(all_users, k=random.randint(0, 3))
    for liker in likers:
        Like.objects.get_or_create(user=liker, post=post)
    if random.random() > 0.5:
        commenter = random.choice(all_users)
        Comment.objects.get_or_create(
            post=post, author=commenter,
            defaults={'content': random.choice(['Great post!', 'Love this!', 'So true!', '💯', 'Totally agree!'])}
        )

print('Demo data seeded! Users: alice, bob, carol, dave, eve (password: pass123)')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting SocialMini at http://127.0.0.1:8000"
echo "   Admin panel: http://127.0.0.1:8000/admin (admin / admin123)"
echo "   Demo users: alice, bob, carol, dave, eve (password: pass123)"
echo ""
python manage.py runserver
