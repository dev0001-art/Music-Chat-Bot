import re

with open('/Users/devmishra/Desktop/Project/new_floating_notes.html', 'r') as f:
    new_notes = f.read()

def replace_in_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace floating notes
    content = re.sub(r'<div class="floating-notes">.*?</div>\n  <div class="radar-bg radar-1">', 
                     new_notes + '\n  <div class="radar-bg radar-1">', 
                     content, flags=re.DOTALL)
    
    if filepath.endswith('auth.html'):
        # Fix font
        content = content.replace(
            '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet" />',
            '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500;600&family=Amita:wght@400;700&display=swap" rel="stylesheet" />'
        )
        
    with open(filepath, 'w') as f:
        f.write(content)

replace_in_file('/Users/devmishra/Desktop/Project/templates/index.html')
replace_in_file('/Users/devmishra/Desktop/Project/templates/auth.html')
