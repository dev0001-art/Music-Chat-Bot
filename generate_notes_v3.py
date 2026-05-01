import random

directions = [
    'float-up', 'float-down', 'float-left', 'float-right',
    'float-top-left', 'float-top-right', 'float-bottom-left', 'float-bottom-right'
]

english_notes = ['♪', '♫', '♩', '♬', '♭', '♮', '♯']
hindi_notes = ['सा', 'रे', 'ग', 'म', 'प', 'ध', 'नि']

output = ['<div class="floating-notes">']

for i in range(250):
    direction = random.choice(directions)
    is_hindi = random.choice([True, False])
    
    if is_hindi:
        note = random.choice(hindi_notes)
        classes = f"float-note {direction} hindi-note"
    else:
        note = random.choice(english_notes)
        classes = f"float-note {direction}"
        
    duration = round(random.uniform(20.0, 45.0), 1)
    delay = round(random.uniform(0.0, 30.0), 1)
    size = round(random.uniform(1.6, 4.0), 1)
    
    if direction == 'float-left' or direction == 'float-right':
        pos_attr = "top"
        pos_val = random.randint(-10, 110)
    else:
        pos_attr = "left"
        if direction in ('float-top-left', 'float-bottom-left'):
            pos_val = random.randint(30, 130)
        elif direction in ('float-top-right', 'float-bottom-right'):
            pos_val = random.randint(-30, 70)
        else:
            pos_val = random.randint(-10, 110)
            
    style = f"{pos_attr}: {pos_val}%; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;"
    output.append(f'    <div class="{classes}" style="{style}">{note}</div>')

output.append('  </div>')

with open('/Users/devmishra/Desktop/Project/new_floating_notes.html', 'w') as f:
    f.write('\n'.join(output))
