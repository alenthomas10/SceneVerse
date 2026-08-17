
import re

file_path = r'e:\SceneVerse\myapp\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

matches = [m.start() for m in re.finditer(r'def\s+edit_project_comment', content)]
print(f"Found {len(matches)} definitions of 'edit_project_comment'")
for pos in matches:
    # find line number
    line_no = content[:pos].count('\n') + 1
    print(f"Line {line_no}")
