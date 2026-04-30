import re

with open('templates/index.html', 'r') as f:
    html = f.read()

with open('new_notes.html', 'r') as f:
    new_notes = f.read()

# Replace everything between <div class="floating-notes"> and </div>\n  <div class="radar-bg radar-1">
pattern = re.compile(r'(<div class="floating-notes">\n).*?(  </div>\n  <div class="radar-bg radar-1">)', re.DOTALL)
new_html = pattern.sub(r'\1' + new_notes + r'\2', html)

with open('templates/index.html', 'w') as f:
    f.write(new_html)
