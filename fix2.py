import re

with open("app.py", "r") as f:
    text = f.read()

correct_func = r"""def analyze_vibe_with_llm(query, conversation_history, user):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_AVAILABLE or not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "You are a music recommendation AI for VibeTune. The user wants music recommendations.\n"
    prompt += f"User language preference: {user.get('language', 'English')}\n"
    prompt += f"User genre preference: {user.get('genre', 'Pop')}\n"
    
    if conversation_history:
        prompt += "\nChat History:\n"
        for turn in conversation_history[-3:]:
            prompt += f"User: {turn['query']}\n"
            prompt += f"AI: {turn['assistant_message']}\n"
            
    prompt += f"\nNew Query: {query}\n"
    prompt += "Analyze the query in context of the history.\n"
    prompt += "Return ONLY a JSON object (no markdown, no backticks) with exactly these keys:\n"
    prompt += "- 'message': A short, conversational response as the AI (1-2 sentences).\n"
    prompt += "- 'mood': The dominant mood (e.g. happy, sad, romantic, calm, energetic, heartbroken, focused).\n"
    prompt += "- 'intent': Any specific genre, artist, or song intent mentioned (e.g. 'Arijit Singh', 'Punjabi Pop', 'workout songs'). If none, leave empty string.\n"
    
    try:"""

# We find the start and the end index manually to be perfectly robust.
start_idx = text.find("def analyze_vibe_with_llm")
end_idx = text.find("    try:", start_idx)

if start_idx != -1 and end_idx != -1:
    new_text = text[:start_idx] + correct_func + "\n" + text[end_idx + 8:]
    with open("app.py", "w") as f:
        f.write(new_text)
    print("SUCCESS")
else:
    print("FAILED TO FIND INDICES")
