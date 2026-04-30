import re

with open('app.py', 'r') as f:
    content = f.read()

import_block = """from urllib.request import Request, urlopen

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
"""
content = content.replace("from urllib.request import Request, urlopen\n", import_block)

llm_func = """
def analyze_vibe_with_llm(query, conversation_history, user):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_AVAILABLE or not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"You are a music recommendation AI for VibeTune. The user wants music recommendations.\n"
    prompt += f"User language preference: {user.get('language', 'English')}\n"
    prompt += f"User genre preference: {user.get('genre', 'Pop')}\n"
    
    if conversation_history:
        prompt += "\nChat History:\n"
        for turn in conversation_history[-3:]: # keep last 3 turns
            prompt += f"User: {turn['query']}\n"
            prompt += f"AI: {turn['assistant_message']}\n"
            
    prompt += f"\nNew Query: {query}\n"
    prompt += "Analyze the query in context of the history.\n"
    prompt += "Return ONLY a JSON object (no markdown, no backticks) with exactly these keys:\n"
    prompt += "- 'message': A short, conversational response as the AI (1-2 sentences).\n"
    prompt += "- 'mood': The dominant mood (e.g. happy, sad, romantic, calm, energetic, heartbroken, focused).\n"
    prompt += "- 'intent': Any specific genre, artist, or song intent mentioned (e.g. 'Arijit Singh', 'Punjabi Pop', 'workout songs'). If none, leave empty string.\n"
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

@app.route("/recommend", methods=["POST"])"""

content = content.replace("@app.route(\"/recommend\", methods=[\"POST\"])", llm_func)

# Now replace the logic inside `recommend`
old_recommend_logic = """    if is_greeting_message(query):
        conversation.append(
            {
                "query": query,
                "assistant_message": build_greeting_reply(user),
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))

    mood = detect_mood(query)
    song_intent = extract_song_intent(query)
    if not mood and not song_intent:
        song_intent = clean_song_query(query)
    mood = mood or infer_mood_from_song_intent(song_intent)
    if not mood:
        conversation.append(
            {
                "query": query,
                "assistant_message": (
                    "I can work with moods like happy, calm, energetic, heartbroken, focused, or romantic. "
                    "You can also type a song name like “Pal Pal Dil Ke Paas” or say “songs like Tum Hi Ho.”"
                ),
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))"""

new_recommend_logic = """    if is_greeting_message(query):
        conversation.append(
            {
                "query": query,
                "assistant_message": build_greeting_reply(user),
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))

    # LLM Integration
    llm_result = analyze_vibe_with_llm(query, conversation, user)
    
    if llm_result:
        mood = llm_result.get("mood", "")
        song_intent = llm_result.get("intent", "")
        assistant_msg = llm_result.get("message", "Here are some songs for you:")
        if not mood and not song_intent:
            mood = detect_mood(query)
            song_intent = extract_song_intent(query)
    else:
        # Fallback to dictionary matching
        mood = detect_mood(query)
        song_intent = extract_song_intent(query)
        if not mood and not song_intent:
            song_intent = clean_song_query(query)
        mood = mood or infer_mood_from_song_intent(song_intent)
        assistant_msg = None # Will be generated later

    if not mood and not song_intent:
        conversation.append(
            {
                "query": query,
                "assistant_message": (
                    "I can work with moods like happy, calm, energetic, heartbroken, focused, or romantic. "
                    "You can also type a song name like “Pal Pal Dil Ke Paas” or say “songs like Tum Hi Ho.”"
                ),
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))"""

content = content.replace(old_recommend_logic, new_recommend_logic)

# We also need to use `assistant_msg` from LLM if available, otherwise generate it.
# Look for where `conversation.append` happens after finding the pool.

old_append = """    if not pool and not reference_song:
        conversation.append(
            {
                "query": query,
                "assistant_message": "I couldn’t find strong Apple Music matches right now. Try another mood, language, or genre.",
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))

    assistant_msg = build_assistant_reply(mood, query, reference_song)"""

new_append = """    if not pool and not reference_song:
        conversation.append(
            {
                "query": query,
                "assistant_message": "I couldn’t find strong Apple Music matches right now. Try another mood, language, or genre.",
                "reference_song": None,
                "recommendations": [],
            }
        )
        set_runtime_values(conversation=conversation, last_query=query, has_more_recommendations=False)
        return redirect(url_for("index"))

    if not assistant_msg:
        assistant_msg = build_assistant_reply(mood, query, reference_song)"""

content = content.replace(old_append, new_append)

with open('app.py', 'w') as f:
    f.write(content)
