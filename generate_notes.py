import random

western = ['♪', '♫', '♩', '♬', '♭', '♯', '♮']
hindi = ['सा', 'रे', 'ग', 'म', 'प', 'ध', 'नि']
directions = ['float-up', 'float-down', 'float-left', 'float-right']

html = []
for i in range(50):
    is_hindi = random.choice([True, False])
    char = random.choice(hindi) if is_hindi else random.choice(western)
    d = random.choice(directions)
    
    dur = random.uniform(12, 30)
    delay = random.uniform(0, 10)
    size = random.uniform(1.5, 3.5)
    
    pos = random.randint(0, 100)
    if d in ['float-up', 'float-down']:
        style = f"left: {pos}%; animation-duration: {dur:.1f}s; animation-delay: {delay:.1f}s; font-size: {size:.1f}rem;"
    else:
        style = f"top: {pos}%; animation-duration: {dur:.1f}s; animation-delay: {delay:.1f}s; font-size: {size:.1f}rem;"
        
    cls = f"float-note {d} hindi-note" if is_hindi else f"float-note {d}"
    html.append(f'    <div class="{cls}" style="{style}">{char}</div>')

with open("notes.html", "w") as f:
    f.write("\n".join(html))
