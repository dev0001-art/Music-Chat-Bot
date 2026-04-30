import random

hindi_notes = ['सा', 'रे', 'ग', 'म', 'प', 'ध', 'नि']
western_notes = ['♪', '♫', '♬', '♭', '♮', '♯', '♩']
directions = [
    ('float-up', 'left', 5, 95),
    ('float-down', 'left', 5, 95),
    ('float-left', 'top', 5, 95),
    ('float-right', 'top', 5, 95),
    ('float-top-left', 'bottom-right', 0, 100),
    ('float-top-right', 'bottom-left', 0, 100),
    ('float-bottom-left', 'top-right', 0, 100),
    ('float-bottom-right', 'top-left', 0, 100)
]

html = []
for i in range(70):
    is_hindi = random.choice([True, False])
    note = random.choice(hindi_notes) if is_hindi else random.choice(western_notes)
    
    dir_class, prop, min_val, max_val = random.choice(directions)
    
    duration = round(random.uniform(15.0, 35.0), 1)
    delay = round(random.uniform(0.0, 15.0), 1)
    size = round(random.uniform(1.8, 3.8), 1)
    
    if prop in ['left', 'top']:
        pos = f"{prop}: {random.randint(min_val, max_val)}%;"
    else:
        # For diagonals, we just need the class, the initial position is set by CSS
        # But we can add a slight offset so they don't all start in the exact corner
        offset_x = random.randint(0, 100)
        offset_y = random.randint(0, 100)
        if 'top' in dir_class:
            pos = f"left: {offset_x}%;" # Starts bottom, anywhere on X
        else:
            pos = f"left: {offset_x}%;" # Starts top, anywhere on X

    cls = f"float-note {dir_class}"
    if is_hindi:
        cls += " hindi-note"
        
    html.append(f'    <div class="{cls}" style="{pos} animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;">{note}</div>')

print("\n".join(html))
