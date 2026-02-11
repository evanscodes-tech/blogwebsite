import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
    print("✅ Superuser 'admin' created with password 'Admin123!'")
else:
    print("✅ Superuser 'admin' already exists")