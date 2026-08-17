import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SceneVerse.settings')
django.setup()

from myapp.models import ArtistComment

print("Searching for suspicious comments...")
suspicious = ArtistComment.objects.filter(comment__contains='{{')
print(f"Found {suspicious.count()} suspicious comments.")
for c in suspicious:
    print(f"ID: {c.id}, Comment: '{c.comment}'")

suspicious2 = ArtistComment.objects.filter(comment__contains='reply.comment')
print(f"Found {suspicious2.count()} suspicious comments with 'reply.comment'.")
for c in suspicious2:
    print(f"ID: {c.id}, Comment: '{c.comment}'")
