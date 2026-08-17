import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SceneVerse.settings')
django.setup()

from myapp.models import ArtistComment

print("Checking ArtistComments...")
comments = ArtistComment.objects.all().order_by('-created_at')[:10]
for c in comments:
    print(f"ID: {c.id}, Parent: {c.parent_id}, Comment: '{c.comment}'")
