import random

directions = [
    'float-up', 'float-down', 'float-left', 'float-right',
    'float-top-left', 'float-top-right', 'float-bottom-left', 'float-bottom-right'
]

english_notes = ['♪', '♫', '♩', '♬', '♭', '♮', '♯']
hindi_notes = ['सा', 'रे', 'ग', 'म', 'प', 'ध', 'नि']

output = ['<div class="floating-notes">']

for i in range(200):
    direction = random.choice(directions)
    is_hindi = random.choice([True, False])
    
    if is_hindi:
        note = random.choice(hindi_notes)
        classes = f"float-note {direction} hindi-note"
    else:
        note = random.choice(english_notes)
        classes = f"float-note {direction}"
        
    duration = round(random.uniform(15.0, 40.0), 1)
    delay = round(random.uniform(0.0, 20.0), 1)
    size = round(random.uniform(1.6, 4.0), 1)
    
    if direction in ('float-up', 'float-down', 'float-top-left', 'float-top-right'):
        pos_attr = "left"
    else:
        pos_attr = "top"
        
    pos_val = random.randint(0, 100)
    
    style = f"{pos_attr}: {pos_val}%; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;"
    output.append(f'    <div class="{classes}" style="{style}">{note}</div>')

output.append('  </div>')

with open('/Users/devmishra/Desktop/Project/new_floating_notes.html', 'w') as f:
    f.write('\n'.join(output))
