import re

with open("app.py", "r") as f:
    text = f.read()

# Replace any occurrence of literal newlines right before a quote in the prompt f-strings
text = re.sub(r'([^\\])\n"', r'\1\\n"', text)

with open("app.py", "w") as f:
    f.write(text)
