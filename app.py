from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os
import tempfile
import uuid
import base64
import time
import re
from json import JSONDecodeError
from urllib.error import URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "vibetune-secret-dev-key-change-in-prod")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.environ.get("VIBETUNE_DATA_DIR") or os.path.join(os.path.expanduser("~"), ".vibetune")
TEMP_DATA_DIR = os.path.join(tempfile.gettempdir(), "vibetune")

SONG_LIBRARY = [
    {"title": "Golden Hour", "artist": "JVKE", "language": "English", "genre": "Pop", "moods": ["romantic", "calm"], "tags": ["soft", "love", "night"]},
    {"title": "Daylight", "artist": "David Kushner", "language": "English", "genre": "Indie", "moods": ["heartbroken", "calm"], "tags": ["sad", "emotional"]},
    {"title": "Blinding Lights", "artist": "The Weeknd", "language": "English", "genre": "Pop", "moods": ["energetic", "happy"], "tags": ["party", "night", "drive"]},
    {"title": "Levitating", "artist": "Dua Lipa", "language": "English", "genre": "Pop", "moods": ["happy", "energetic"], "tags": ["dance", "fun"]},
    {"title": "Heat Waves", "artist": "Glass Animals", "language": "English", "genre": "Indie", "moods": ["calm", "romantic"], "tags": ["dreamy", "late night"]},
    {"title": "Believer", "artist": "Imagine Dragons", "language": "English", "genre": "Rock", "moods": ["energetic", "focused"], "tags": ["gym", "power"]},
    {"title": "Perfect", "artist": "Ed Sheeran", "language": "English", "genre": "Ballad", "moods": ["romantic"], "tags": ["wedding", "love"]},
    {"title": "Until I Found You", "artist": "Stephen Sanchez", "language": "English", "genre": "Retro Pop", "moods": ["romantic", "calm"], "tags": ["classic", "soft"]},
    {"title": "Kesariya", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic"], "tags": ["love", "warm"]},
    {"title": "Apna Bana Le", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic", "calm"], "tags": ["soft", "dreamy"]},
    {"title": "Ilahi", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["happy", "energetic"], "tags": ["travel", "free"]},
    {"title": "Channa Mereya", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["heartbroken"], "tags": ["sad", "breakup"]},
    {"title": "Shayad", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic", "heartbroken"], "tags": ["longing", "soft"]},
    {"title": "Malang Sajna", "artist": "Sachet-Parampara", "language": "Hindi", "genre": "Pop", "moods": ["happy", "romantic"], "tags": ["celebration", "dance"]},
    {"title": "Excuses", "artist": "AP Dhillon", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["calm", "focused"], "tags": ["late night", "drive"]},
    {"title": "Brown Munde", "artist": "AP Dhillon", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["energetic", "happy"], "tags": ["party", "confidence"]},
    {"title": "Insane", "artist": "AP Dhillon", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["focused", "calm"], "tags": ["smooth", "night"]},
    {"title": "Khabbi Seat", "artist": "Ammy Virk", "language": "Punjabi", "genre": "Punjabi", "moods": ["romantic"], "tags": ["love", "sweet"]},
    {"title": "Qismat", "artist": "Ammy Virk", "language": "Punjabi", "genre": "Punjabi", "moods": ["heartbroken"], "tags": ["sad", "pain", "breakup"]},
    {"title": "So High", "artist": "Sidhu Moose Wala", "language": "Punjabi", "genre": "Punjabi Rap", "moods": ["energetic", "focused"], "tags": ["hype", "confidence", "drive"]},
    {"title": "Born To Shine", "artist": "Diljit Dosanjh", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["happy", "energetic"], "tags": ["style", "party", "confidence"]},
    {"title": "Lover", "artist": "Diljit Dosanjh", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["romantic", "calm"], "tags": ["soft", "love", "dreamy"]},
    {"title": "Do You Know", "artist": "Diljit Dosanjh", "language": "Punjabi", "genre": "Punjabi Pop", "moods": ["romantic", "happy"], "tags": ["love", "sweet", "feel good"]},
    {"title": "Pasoori", "artist": "Ali Sethi and Shae Gill", "language": "Punjabi", "genre": "Fusion", "moods": ["calm", "romantic"], "tags": ["soulful", "viral", "soft"]},
    {"title": "Titliaan", "artist": "Afsana Khan", "language": "Punjabi", "genre": "Punjabi", "moods": ["heartbroken"], "tags": ["sad", "pain", "emotional"]},
    {"title": "Raatan Lambiyan", "artist": "Jubin Nautiyal and Asees Kaur", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic", "calm"], "tags": ["night", "love", "soft"]},
    {"title": "Tum Hi Ho", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["heartbroken", "romantic"], "tags": ["sad", "love", "classic"]},
    {"title": "Ghungroo", "artist": "Arijit Singh and Shilpa Rao", "language": "Hindi", "genre": "Bollywood", "moods": ["happy", "energetic"], "tags": ["dance", "party", "travel"]},
    {"title": "Raabta", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic", "calm"], "tags": ["love", "soft", "warm"]},
    {"title": "Satranga", "artist": "Arijit Singh", "language": "Hindi", "genre": "Bollywood", "moods": ["romantic", "heartbroken"], "tags": ["longing", "soft", "sad"]},
    {"title": "Shape of You", "artist": "Ed Sheeran", "language": "English", "genre": "Pop", "moods": ["happy", "energetic"], "tags": ["dance", "party", "fun"]},
    {"title": "Someone Like You", "artist": "Adele", "language": "English", "genre": "Ballad", "moods": ["heartbroken", "calm"], "tags": ["sad", "emotional", "slow"]},
    {"title": "Night Changes", "artist": "One Direction", "language": "English", "genre": "Pop", "moods": ["calm", "romantic"], "tags": ["night", "soft", "nostalgic"]},
    {"title": "Counting Stars", "artist": "OneRepublic", "language": "English", "genre": "Pop Rock", "moods": ["focused", "energetic"], "tags": ["drive", "hype", "work"]},
    {"title": "Perfect Duet", "artist": "Ed Sheeran and Beyonce", "language": "English", "genre": "Ballad", "moods": ["romantic"], "tags": ["love", "wedding", "soft"]},
]

DEFAULT_RECOMMENDATION_COUNT = 5
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
DEEZER_SEARCH_URL = "https://api.deezer.com/search"
PREVIEW_CACHE = {}
RUNTIME_STATE = {}

LANGUAGE_CONFIGS = {
    "english": {"country": "US", "hint": "english songs"},
    "hindi": {"country": "IN", "hint": "hindi songs bollywood"},
    "punjabi": {"country": "IN", "hint": "punjabi songs"},
}

GENRE_INTENT_MAP = {
    "new": ["new songs", "latest hits", "recent releases"],
    "latest": ["latest songs", "new releases", "trending tracks"],
    "old": ["old songs", "classic hits", "retro songs"],
    "classic": ["classic songs", "timeless hits", "golden era songs"],
    "party": ["party songs", "dance hits", "celebration songs"],
    "dance": ["dance songs", "club hits", "party anthems"],
    "sad": ["sad songs", "emotional songs", "heartbreak music"],
    "romantic": ["romantic songs", "love songs", "soft romantic music"],
    "chill": ["chill songs", "relaxing music", "easy listening"],
    "lofi": ["lofi beats", "chill lofi", "study lofi"],
    "study": ["study music", "focus songs", "concentration music"],
    "workout": ["workout songs", "gym songs", "high energy tracks"],
    "devotional": ["devotional songs", "spiritual music", "bhajan songs"],
    "indie": ["indie songs", "indie pop", "independent music"],
    "pop": ["pop songs", "popular hits", "pop music"],
    "rock": ["rock songs", "rock anthems", "classic rock"],
    "rap": ["rap songs", "hip hop hits", "rap music"],
    "hiphop": ["hip hop songs", "rap hits", "hip hop music"],
}

MOOD_PROFILES = {
    "happy": {
        "aliases": ["happy", "joyful", "good", "sunny", "cheerful", "excited"],
        "search_terms": ["upbeat pop", "feel good hits", "happy indie"],
        "response_lead": "You sound bright and upbeat, so I leaned into warm hooks and energetic melodies.",
    },
    "calm": {
        "aliases": ["calm", "peaceful", "relaxed", "soft", "easy", "quiet"],
        "search_terms": ["chill acoustic", "soft ambient", "calm indie"],
        "response_lead": "This feels like a softer mood, so I looked for gentler songs with room to breathe.",
    },
    "heartbroken": {
        "aliases": ["sad", "heartbroken", "down", "cry", "lonely", "broken", "breakup"],
        "search_terms": ["sad songs", "melancholy pop", "emotional indie"],
        "response_lead": "That mood deserves something honest, so these picks lean reflective and emotional.",
    },
    "focused": {
        "aliases": ["focused", "study", "work", "productive", "concentrate", "deep"],
        "search_terms": ["focus instrumental", "study beats", "ambient electronic"],
        "response_lead": "You sound locked in, so I prioritized songs that help you stay steady.",
    },
    "energetic": {
        "aliases": ["energetic", "hyped", "gym", "power", "party", "fast"],
        "search_terms": ["workout hits", "dance pop", "high energy"],
        "response_lead": "You want momentum, so I went for bigger rhythm and faster energy.",
    },
    "romantic": {
        "aliases": ["romantic", "love", "date", "crush", "dreamy", "intimate"],
        "search_terms": ["romantic songs", "dreamy pop", "love ballads"],
        "response_lead": "That mood called for something warm and intimate, with a little glow to it.",
    },
}

MOOD_SIGNALS = {
    "happy": {
        "phrases": ["feel good", "good mood", "cheer me up", "make me smile", "good vibes", "fun songs"],
        "words": ["happy", "joyful", "cheerful", "sunny", "bright", "smile", "fun", "playful", "positive", "celebration"],
    },
    "calm": {
        "phrases": ["calm down", "relax me", "late night", "slow songs", "peaceful songs", "soft songs"],
        "words": ["calm", "peaceful", "relaxed", "soft", "quiet", "gentle", "slow", "chill", "soothing", "stress", "stressed"],
    },
    "heartbroken": {
        "phrases": ["broken heart", "heart break", "miss someone", "crying songs", "sad songs", "feeling low"],
        "words": ["sad", "heartbroken", "down", "cry", "crying", "lonely", "broken", "hurt", "pain", "upset", "miss"],
    },
    "focused": {
        "phrases": ["study music", "study songs", "work music", "deep focus", "help me focus", "concentration music"],
        "words": ["focused", "focus", "study", "work", "productive", "concentrate", "deep", "coding", "reading", "background"],
    },
    "energetic": {
        "phrases": ["gym songs", "workout songs", "pump me up", "high energy", "party songs", "dance songs"],
        "words": ["energetic", "hyped", "gym", "power", "party", "fast", "workout", "dance", "boost", "motivation", "motivated", "running"],
    },
    "romantic": {
        "phrases": ["love songs", "date night", "romantic songs", "for my crush", "falling in love", "dreamy songs"],
        "words": ["romantic", "love", "date", "crush", "dreamy", "intimate", "affection", "sweet", "loving"],
    },
}


def normalize_text(value):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (value or "").lower())).strip()


def is_usable_dir(path):
    return os.path.isdir(path) and os.access(path, os.W_OK)


def resolve_users_file():
    env_file = os.environ.get("VIBETUNE_USERS_FILE")
    if env_file:
        return env_file

    project_file = os.path.join(BASE_DIR, "users_db.json")
    if os.path.exists(project_file):
        if os.access(project_file, os.W_OK):
            return project_file
    elif os.access(BASE_DIR, os.W_OK):
        return project_file

    home_parent = os.path.dirname(DEFAULT_DATA_DIR)
    if is_usable_dir(DEFAULT_DATA_DIR) or os.access(home_parent, os.W_OK):
        return os.path.join(DEFAULT_DATA_DIR, "users_db.json")

    return os.path.join(TEMP_DATA_DIR, "users_db.json")


USERS_FILE = resolve_users_file()


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (JSONDecodeError, OSError):
        return {}


def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)


def is_gmail_address(email):
    return re.fullmatch(r"[^@\s]+@gmail\.com", (email or "").strip().lower()) is not None


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = load_users().get(user_id)
    if user and not is_gmail_address(user.get("email")):
        return None
    return user



def require_user():
    user = current_user()
    if not user:
        flash("Please log in to continue.", "error")
        return None
    return user


def escape_regex(value):
    return re.escape(value)


def is_greeting_message(message):
    normalized = normalize_text(message)
    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "heyy",
        "good morning",
        "good afternoon",
        "good evening",
    }
    return normalized in greetings


def build_greeting_reply(user):
    name_part = f" {user.get('name', '')}" if user.get("name") else ""
    return f"Hello{name_part}. Tell me your mood, your favorite type of song, or even a song name, and I’ll find something for you."


def detect_mood(message):
    normalized = normalize_text(message)
    scores = {mood_key: 0 for mood_key in MOOD_PROFILES}

    for mood_key, mood in MOOD_PROFILES.items():
        for alias in mood["aliases"]:
            if normalize_text(alias) in normalized:
                scores[mood_key] += 3

    for mood_key, signal_group in MOOD_SIGNALS.items():
        for phrase in signal_group["phrases"]:
            if normalize_text(phrase) in normalized:
                scores[mood_key] += 4

        for word in signal_group["words"]:
            pattern = rf"\b{escape_regex(normalize_text(word))}\b"
            matches = re.findall(pattern, normalized)
            if matches:
                scores[mood_key] += len(matches) * 2

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not ranked or ranked[0][1] == 0:
        return ""

    return ranked[0][0]


def clean_song_query(value):
    return re.sub(r"[?.!,]+$", "", value).strip()


COMPACT_SONG_QUERY_VARIANTS = {
    "koina": "koi na",
    "koinah": "koi na",
    "palpaldilkepaas": "pal pal dil ke paas",
    "tumhiho": "tum hi ho",
}


def build_song_query_variants(song_intent):
    cleaned = clean_song_query(song_intent)
    normalized = normalize_text(cleaned)
    compact = re.sub(r"\s+", "", normalized)
    variants = [cleaned]

    mapped = COMPACT_SONG_QUERY_VARIANTS.get(compact)
    if mapped:
        variants.append(mapped)

    return list(dict.fromkeys([variant for variant in variants if variant]))


def detect_explicit_mood_only(normalized):
    return any(
        normalize_text(phrase) in normalized
        for signal_group in MOOD_SIGNALS.values()
        for phrase in signal_group["phrases"]
    )


def extract_song_intent(message):
    normalized = message.strip()
    lowered = normalize_text(message)
    trigger_patterns = [
        r"songs?\s+like\s+(.+)",
        r"recommend\s+.*like\s+(.+)",
        r"play\s+(.+)",
        r"listen\s+to\s+(.+)",
        r"similar\s+to\s+(.+)",
    ]

    for pattern in trigger_patterns:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match and match.group(1):
            return clean_song_query(match.group(1))

    filler_words = {
        "i",
        "want",
        "need",
        "give",
        "me",
        "some",
        "song",
        "songs",
        "recommend",
        "music",
        "playlist",
        "play",
        "please",
        "any",
    }

    tokens = [token for token in lowered.split(" ") if token]
    meaningful_tokens = [token for token in tokens if token not in filler_words]
    if len(meaningful_tokens) >= 2 and not detect_explicit_mood_only(lowered):
        return clean_song_query(" ".join(meaningful_tokens))

    return ""


def infer_mood_from_song_intent(song_intent):
    if not song_intent:
        return ""

    query = normalize_text(song_intent)
    if re.search(r"(dil|love|ishq|pyaar|romance|romantic|jaan|saath|pal pal)", query):
        return "romantic"
    if re.search(r"(sad|cry|broken|judai|lonely|pain|heart)", query):
        return "heartbroken"
    if re.search(r"(dance|party|power|run|energy|gym|beat)", query):
        return "energetic"
    if re.search(r"(calm|peace|soft|night|slow|soul)", query):
        return "calm"
    if re.search(r"(study|focus|work|lofi|instrumental)", query):
        return "focused"

    return "romantic"


def build_mood_lead_line(mood_key, song_intent):
    song_part = f' I also picked up "{song_intent}" in your request.' if song_intent else ""
    lines = {
        "happy": f"Looks like you're in a happy mood.{song_part} Let me find songs that match that vibe...",
        "calm": f"Looks like you want to relax.{song_part} Let me find songs that match that vibe...",
        "heartbroken": f"Looks sad...{song_part} Let me find songs that match that vibe...",
        "focused": f"Looks like you want to focus.{song_part} Let me find songs that match that vibe...",
        "energetic": f"Looks like you need some energy.{song_part} Let me find songs that match that vibe...",
        "romantic": f"Looks like you're in love.{song_part} Let me find songs that match that vibe...",
    }
    return lines.get(mood_key, "Let me find songs for your vibe...")


def get_language_config(user):
    language_pref = (user.get("language") or "").strip().lower()
    
    if language_pref == "any":
        # For "Any" language, return config that searches across multiple countries
        return {
            "country": "multi", 
            "hint": "multilingual",
            "countries": ["US", "IN", "GB", "CA", "AU"]  # Multiple countries for diverse languages
        }
    
    return LANGUAGE_CONFIGS.get(language_pref, {"country": "US", "hint": ""})


def get_genre_hints(genre_value):
    normalized = normalize_text(genre_value or "")
    if not normalized:
        return {"primary": "", "related": []}

    compact = re.sub(r"\s+", "", normalized)
    mapped = GENRE_INTENT_MAP.get(compact) or GENRE_INTENT_MAP.get(normalized)
    if mapped:
        return {"primary": mapped[0], "related": mapped[1:]}

    return {"primary": normalized, "related": []}


def build_detailed_query(message, user, language_config):
    cleaned_message = normalize_text(message)
    genre_hints = get_genre_hints(user.get("genre", ""))
    return " ".join(
        part for part in [cleaned_message, language_config.get("hint", ""), genre_hints["primary"]] if part
    )


def build_recommendation_intro(mood_key, user):
    mood = MOOD_PROFILES[mood_key]
    name_part = f"{user.get('name')}, " if user.get("name") else ""
    language_part = f" I kept the picks closer to {user.get('language')} songs." if user.get("language") else ""
    genre_hints = get_genre_hints(user.get("genre", ""))
    genre_part = f" Your {genre_hints['primary']} preference helped steer the blend." if genre_hints["primary"] else ""
    return f"{name_part}{mood['response_lead']}{language_part}{genre_part}"


def get_recommendation_count(message):
    word_count = len([word for word in message.strip().split() if word])
    if word_count >= 18:
        return 12
    if word_count >= 10:
        return 8
    return 5


def build_apple_music_search_url(track_name, artist_name, country="us"):
    query = quote(f"{track_name} {artist_name}")
    return f"https://music.apple.com/{country.lower()}/search?term={query}"


def build_spotify_search_url(track_name, artist_name):
    query = quote(f"{track_name} {artist_name}")
    return f"https://open.spotify.com/search/{query}"


def fetch_deezer_preview_url(track_name, artist_name):
    cache_key = normalize_text(f"{track_name} {artist_name}")
    if cache_key in PREVIEW_CACHE:
        return PREVIEW_CACHE[cache_key]

    params = urlencode(
        {
            "q": f'track:"{track_name}" artist:"{artist_name}"',
            "limit": "1",
        }
    )
    req = Request(f"{DEEZER_SEARCH_URL}?{params}", method="GET")
    try:
        with urlopen(req, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))
        items = payload.get("data") or []
        preview_url = (items[0].get("preview") if items else "") or ""
        PREVIEW_CACHE[cache_key] = preview_url
        return preview_url
    except (URLError, OSError, ValueError, JSONDecodeError):
        PREVIEW_CACHE[cache_key] = ""
        return ""


def resolve_preview_url(preview_url, track_name, artist_name):
    if preview_url:
        return preview_url
    return fetch_deezer_preview_url(track_name, artist_name)


def search_itunes(term, limit=10, country="US"):
    params = urlencode(
        {
            "term": term,
            "media": "music",
            "entity": "song",
            "country": country,
            "limit": str(limit),
        }
    )
    req = Request(f"{ITUNES_SEARCH_URL}?{params}", method="GET")
    with urlopen(req, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("results") or []


def get_song_search_countries(user):
    config = get_language_config(user)
    
    if config["country"] == "multi":
        # For "Any" language, return all the configured countries
        return config["countries"]
    else:
        preferred = config["country"]
        return list(dict.fromkeys([preferred, "IN", "US", "GB"]))


def normalize_itunes_track(track, country):
    title = track.get("trackName") or "Unknown Title"
    artist = track.get("artistName") or "Unknown Artist"
    album = track.get("collectionName") or "Single"
    genre = track.get("primaryGenreName") or "Music"
    preview_url = resolve_preview_url((track.get("previewUrl") or "").strip(), title, artist)
    spotify_url = build_spotify_search_url(title, artist)
    apple_url = build_apple_music_search_url(title, artist, country)
    return {
        "title": title,
        "artist": artist,
        "language": "Music",
        "genre": genre,
        "album": album,
        "website_url": spotify_url,
        "app_url": "",
        "play_url": preview_url or spotify_url,
        "preview_url": preview_url,
        "spotify_url": spotify_url,
        "apple_url": apple_url,
        "track_id": str(track.get("trackId") or uuid.uuid4()),
    }


def get_recommendations(search_terms, country="US"):
    raw_tracks = []
    for term in search_terms[:4]:
        raw_tracks.extend(search_itunes(term, limit=12, country=country))

    seen = set()
    tracks = []
    for track in raw_tracks:
        if track.get("wrapperType") != "track" or track.get("kind") != "song":
            continue

        key = f"{track.get('trackName', '')}-{track.get('artistName', '')}".lower()
        if key in seen:
            continue

        seen.add(key)
        tracks.append(normalize_itunes_track(track, country))

    return tracks[:24]


def infer_mood_from_track(track, fallback_mood):
    if not track:
        return fallback_mood

    haystack = normalize_text(
        " ".join(
            [
                track.get("title", ""),
                track.get("artist", ""),
                track.get("album", ""),
                track.get("genre", ""),
            ]
        )
    )
    if re.search(r"(dance|electronic|edm|hip hop|rap|workout|party|pop)", haystack):
        return "energetic"
    if re.search(r"(sad|heartbreak|breakup|blues|melancholy)", haystack):
        return "heartbroken"
    if re.search(r"(love|romantic|romance|dil|pyaar|ishq)", haystack):
        return "romantic"
    if re.search(r"(acoustic|ambient|instrumental|classical|soundtrack|lofi|chill)", haystack):
        return "calm"
    if re.search(r"(focus|study|meditation)", haystack):
        return "focused"

    return fallback_mood


def build_search_terms(message, user, mood_key, song_intent, reference_song=None):
    language_config = get_language_config(user)
    genre_hints = get_genre_hints(user.get("genre", ""))
    mood = MOOD_PROFILES[mood_key]
    song_variants = build_song_query_variants(song_intent)
    if reference_song:
        reference_genre = reference_song.get("genre", "")
        reference_artist = reference_song.get("artist", "")
        return [
            term
            for term in [
                *song_variants,
                f"{reference_genre} {language_config.get('hint', '')}",
                *[f"{term} {language_config.get('hint', '')}" for term in mood["search_terms"]],
                f"{reference_artist} {reference_genre}",
                f"{language_config.get('hint', '')} {genre_hints['primary']}" if genre_hints["primary"] else "",
            ]
            if term.strip()
        ]

    return [
        term
        for term in [
            *song_variants,
            build_detailed_query(message, user, language_config),
            f"{language_config['hint']} {genre_hints['primary']}" if language_config.get("hint") and genre_hints["primary"] else "",
            language_config.get("hint", ""),
            genre_hints["primary"],
            *genre_hints["related"],
            *mood["search_terms"],
        ]
        if term
    ]


def fetch_recommendation_pool(query, user, mood_key, song_intent, reference_song=None):
    language_config = get_language_config(user)
    search_terms = build_search_terms(query, user, mood_key, song_intent, reference_song)
    
    if language_config["country"] == "multi":
        # For "Any" language, search across multiple countries
        all_results = []
        for country in language_config["countries"]:
            results = get_recommendations(search_terms, country)
            all_results.extend(results)
        return all_results
    else:
        return get_recommendations(search_terms, language_config["country"])


def fetch_direct_song_pool(song_intent, user):
    tracks = []
    seen = set()
    for country in get_song_search_countries(user):
        for query in build_song_query_variants(song_intent):
            for track in search_itunes(query, limit=12, country=country):
                if track.get("wrapperType") != "track" or track.get("kind") != "song":
                    continue

                key = f"{track.get('trackName', '')}-{track.get('artistName', '')}".lower()
                if key in seen:
                    continue

                seen.add(key)
                tracks.append(normalize_itunes_track(track, country))

    return tracks[:24]


def find_reference_song(song_intent, user):
    if not song_intent:
        return None

    for country in get_song_search_countries(user):
        for query in build_song_query_variants(song_intent):
            tracks = search_itunes(query, limit=12, country=country)
            for track in tracks:
                if track.get("wrapperType") == "track" and track.get("kind") == "song":
                    return normalize_itunes_track(track, country)

    return None


def remove_duplicate_track(pool, reference_song):
    if not reference_song:
        return pool

    reference_key = (
        normalize_text(reference_song.get("title", "")),
        normalize_text(reference_song.get("artist", "")),
    )
    return [
        track for track in pool
        if (
            normalize_text(track.get("title", "")),
            normalize_text(track.get("artist", "")),
        ) != reference_key
    ]


def paginate_recommendations(pool, offset=0, count=DEFAULT_RECOMMENDATION_COUNT):
    picks = pool[offset:offset + count]
    has_more = offset + count < len(pool)
    return picks, has_more


def normalize_track(song):
    title = song.get("title", "")
    artist = song.get("artist", "")
    spotify_url = (song.get("spotify_url") or build_spotify_search_url(title, artist)).strip()
    website_url = spotify_url
    preview_url = resolve_preview_url((song.get("preview_url") or "").strip(), title, artist)
    apple_url = (song.get("apple_url") or build_apple_music_search_url(title, artist, "us")).strip()
    play_url = preview_url or spotify_url

    return {
        "title": title,
        "artist": artist,
        "language": song.get("language", "Music"),
        "genre": song.get("genre", song.get("album", "Single")),
        "album": song.get("album", "Single"),
        "website_url": website_url,
        "app_url": "",
        "play_url": play_url,
        "preview_url": preview_url,
        "spotify_url": spotify_url,
        "apple_url": apple_url,
        "track_id": song.get("track_id", ""),
    }


def compact_track(song):
    if not song:
        return None
    normalized = normalize_track(song)
    return {
        "title": normalized.get("title", ""),
        "artist": normalized.get("artist", ""),
        "language": normalized.get("language", "Music"),
        "genre": normalized.get("genre", "Music"),
        "album": normalized.get("album", "Single"),
        "preview_url": normalized.get("preview_url", ""),
        "track_id": normalized.get("track_id", ""),
    }


def hydrate_conversation(conversation):
    hydrated = []
    for turn in conversation:
        hydrated.append(
            {
                "query": turn.get("query", ""),
                "assistant_message": turn.get("assistant_message", ""),
                "reference_song": normalize_track(turn.get("reference_song")) if turn.get("reference_song") else None,
                "recommendations": [normalize_track(song) for song in turn.get("recommendations", [])],
            }
        )
    return hydrated


def get_conversation():
    user_id = session.get("user_id")
    if not user_id:
        return []
    state = RUNTIME_STATE.get(user_id, {})
    conversation = state.get("conversation", [])
    return conversation if isinstance(conversation, list) else []


def get_runtime_value(key, default=None):
    user_id = session.get("user_id")
    if not user_id:
        return default
    return RUNTIME_STATE.get(user_id, {}).get(key, default)


def set_runtime_values(**kwargs):
    user_id = session.get("user_id")
    if not user_id:
        return
    state = RUNTIME_STATE.setdefault(user_id, {})
    state.update(kwargs)


def clear_runtime_values(*keys):
    user_id = session.get("user_id")
    if not user_id:
        return
    state = RUNTIME_STATE.setdefault(user_id, {})
    for key in keys:
        state.pop(key, None)


@app.route("/")
def index():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    normalized_user = dict(user)
    normalized_user["favorites"] = [normalize_track(song) for song in user.get("favorites", [])]

    conversation = hydrate_conversation(get_conversation())
    query = get_runtime_value("last_query", "")
    has_more = get_runtime_value("has_more_recommendations", False)
    return render_template(
        "index.html",
        user=normalized_user,
        conversation=conversation,
        last_query=query,
        has_more=has_more,
    )


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("auth.html", mode="login")
        if not is_gmail_address(email):
            flash("Invalid email.", "error")
            return render_template("auth.html", mode="login")

        users = load_users()
        for user_id, user in users.items():
            if user.get("email") == email and check_password_hash(user["password_hash"], password):
                session["user_id"] = user_id
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for("index"))

        flash("Invalid email or password.", "error")
    return render_template("auth.html", mode="login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("auth.html", mode="signup")
        if not is_gmail_address(email):
            flash("Invalid email.", "error")
            return render_template("auth.html", mode="signup")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth.html", mode="signup")

        users = load_users()
        if any(user.get("email") == email for user in users.values()):
            flash("That email is already registered.", "error")
            return render_template("auth.html", mode="signup")

        user_id = str(uuid.uuid4())
        users[user_id] = {
            "id": user_id,
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password, method="pbkdf2:sha256"),
            "language": "English",
            "genre": "Pop",
            "favorites": [],
        }
        save_users(users)
        session["user_id"] = user_id
        flash("Account created successfully.", "success")
        return redirect(url_for("index"))

    return render_template("auth.html", mode="signup")


@app.route("/logout", methods=["POST"])
def logout():
    user_id = session.get("user_id")
    if user_id:
        RUNTIME_STATE.pop(user_id, None)
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/recently-played", methods=["POST"])
def recently_played():
    user = require_user()
    if not user:
        return jsonify({"success": False})

    try:
        data = request.get_json()
        title = data.get("title", "")
        artist = data.get("artist", "")
        preview_url = data.get("preview_url", "")
        
        if title and artist:
            users = load_users()
            saved_user = users.get(session["user_id"])
            if saved_user:
                # Initialize recently played list if it doesn't exist
                if "recently_played" not in saved_user:
                    saved_user["recently_played"] = []
                
                # Add song to recently played (avoid duplicates)
                song_info = {
                    "title": title,
                    "artist": artist,
                    "preview_url": preview_url,
                    "played_at": time.time()
                }
                
                # Remove if already exists, then add to beginning
                saved_user["recently_played"] = [
                    song for song in saved_user["recently_played"] 
                    if not (song.get("title") == title and song.get("artist") == artist)
                ]
                saved_user["recently_played"].insert(0, song_info)
                
                # Keep only last 10 songs
                saved_user["recently_played"] = saved_user["recently_played"][:10]
                
                save_users(users)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False})


@app.route("/recently-played-section")
def recently_played_section():
    user = require_user()
    if not user:
        return ""
    
    # Return just the recently played list HTML
    if user.get("recently_played"):
        html = '<div class="recently-played-list">'
        for song in user["recently_played"][:5]:
            html += f'''
            <div class="recent-song-item">
              <div class="recent-song-info">
                <h4>{song.get("title", "")}</h4>
                <p>{song.get("artist", "")}</p>
              </div>
              <button class="track-link play-inline-btn" 
                      type="button"
                      data-preview-url="{song.get('preview_url', '')}"
                      data-title="{song.get('title', '')}"
                      data-artist="{song.get('artist', '')}">
                Play
              </button>
            </div>
            '''
        html += '</div>'
        return html
    else:
        return '<div class="recently-played-list"><p class="recently-empty">No songs played yet. Start exploring music!</p></div>'


@app.route("/preferences", methods=["POST"])
def preferences():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    users = load_users()
    saved_user = users.get(session["user_id"])
    if not saved_user:
        session.clear()
        flash("User account not found.", "error")
        return redirect(url_for("login"))

    saved_user["language"] = request.form.get("language", "English").strip() or "English"
    selected_genre = request.form.get("genre", "Pop").strip() or "Pop"
    print(f"DEBUG: Selected genre = {selected_genre}")
    saved_user["genre"] = selected_genre
    save_users(users)
    print("DEBUG: Users saved")
    
    # Test: Just show a simple message first
    flash(f"Genre saved: {selected_genre}! Test working.", "success")
    print(f"DEBUG: Genre {selected_genre} saved successfully")
    return redirect(url_for("index"))



def analyze_vibe_with_llm(query, conversation_history, user):
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

@app.route("/recommend", methods=["POST"])
def recommend():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    query = request.form.get("query", "").strip()
    if not query:
        flash("Tell VibeTune how you feel first.", "error")
        return redirect(url_for("index"))

    conversation = get_conversation()

    if is_greeting_message(query):
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
        return redirect(url_for("index"))

    recommendation_count = get_recommendation_count(query)
    try:
        reference_song = find_reference_song(song_intent, user)
        mood = infer_mood_from_track(reference_song, mood)
        pool = fetch_recommendation_pool(query, user, mood, song_intent, reference_song)
        if not pool and song_intent:
            pool = fetch_direct_song_pool(song_intent, user)
            if not reference_song and pool:
                reference_song = pool[0]
                mood = infer_mood_from_track(reference_song, mood)
        pool = remove_duplicate_track(pool, reference_song)
    except URLError:
        reference_song = None
        pool = []

    if not pool and not reference_song:
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

    picks, has_more = paginate_recommendations(pool, offset=0, count=recommendation_count)
    set_runtime_values(
        recommendation_pool=[compact_track(song) for song in pool],
        last_mood=mood,
        last_query=query,
        last_song_intent=song_intent,
        last_recommendation_count=recommendation_count,
        recommendation_offset=0,
        has_more_recommendations=has_more,
    )

    turn = {
        "query": query,
        "assistant_message": (
            (
                f'I found "{reference_song["title"]}" by {reference_song["artist"]} first. '
                if reference_song else ""
            )
            + f"{build_recommendation_intro(mood, user)} "
            f"I found {min(recommendation_count, len(pool))} songs based on your request."
        ),
        "reference_song": compact_track(reference_song) if reference_song else None,
        "recommendations": [compact_track(song) for song in picks],
    }
    conversation.append(turn)
    set_runtime_values(conversation=conversation)
    return redirect(url_for("index"))


@app.route("/recommend/more", methods=["POST"])
def recommend_more():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    query = (get_runtime_value("last_query", "") or "").strip()
    if not query:
        flash("Ask for songs first, then use More songs.", "error")
        return redirect(url_for("index"))

    recommendation_count = get_runtime_value("last_recommendation_count") or get_recommendation_count(query)
    next_offset = get_runtime_value("recommendation_offset", 0) + recommendation_count
    pool = get_runtime_value("recommendation_pool", [])
    mood = get_runtime_value("last_mood", detect_mood(query))
    picks, has_more = paginate_recommendations(pool, offset=next_offset, count=recommendation_count)
    if not picks:
        flash("I’ve reached the end of the current Apple Music batch. Try a more detailed mood or a different genre for fresh results.", "error")
        set_runtime_values(has_more_recommendations=False)
        return redirect(url_for("index"))

    set_runtime_values(last_mood=mood, recommendation_offset=next_offset, has_more_recommendations=has_more)

    conversation = get_conversation()
    if conversation:
        latest_turn = conversation[-1]
        existing = latest_turn.get("recommendations", [])
        existing.extend([compact_track(song) for song in picks])
        latest_turn["recommendations"] = existing
        conversation[-1] = latest_turn
        set_runtime_values(conversation=conversation)

    flash(f"Here are {len(picks)} more Apple Music songs for the same mood.", "success")
    return redirect(url_for("index"))


@app.route("/conversation/clear", methods=["POST"])
def clear_conversation():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    set_runtime_values(
        conversation=[],
        recommendation_pool=[],
        recommendation_offset=0,
        has_more_recommendations=False,
        last_query="",
        last_mood="",
    )
    clear_runtime_values("reference_song")
    flash("Conversation cleared.", "success")
    return redirect(url_for("index"))


@app.route("/favorite", methods=["POST"])
def favorite():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    artist = request.form.get("artist", "").strip()
    language = request.form.get("language", "").strip()
    genre = request.form.get("genre", "").strip()
    album = request.form.get("album", "").strip()
    website_url = request.form.get("website_url", "").strip()
    app_url = request.form.get("app_url", "").strip()
    preview_url = request.form.get("preview_url", "").strip()
    spotify_url = request.form.get("spotify_url", "").strip()
    apple_url = request.form.get("apple_url", "").strip()

    if not title or not artist:
        flash("Could not save that song.", "error")
        return redirect(url_for("index"))

    users = load_users()
    saved_user = users.get(session["user_id"])
    if not saved_user:
        session.clear()
        flash("User account not found.", "error")
        return redirect(url_for("login"))

    favorites = saved_user.get("favorites", [])
    exists = any(song["title"] == title and song["artist"] == artist for song in favorites)
    if exists:
        flash("Song already in favorites.", "error")
        return redirect(url_for("index"))

    favorites.insert(
        0,
        {
            "title": title,
            "artist": artist,
            "language": language,
            "genre": genre,
            "album": album,
            "website_url": website_url,
            "app_url": app_url,
            "preview_url": preview_url,
            "spotify_url": spotify_url,
            "apple_url": apple_url,
        },
    )
    saved_user["favorites"] = favorites[:12]
    save_users(users)
    flash(f"Saved {title} to favorites.", "success")
    return redirect(url_for("index"))


@app.route("/favorite/delete", methods=["POST"])
def delete_favorite():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    artist = request.form.get("artist", "").strip()

    users = load_users()
    saved_user = users.get(session["user_id"])
    if not saved_user:
        session.clear()
        flash("User account not found.", "error")
        return redirect(url_for("login"))

    favorites = saved_user.get("favorites", [])
    saved_user["favorites"] = [
        song for song in favorites if not (song["title"] == title and song["artist"] == artist)
    ]
    save_users(users)
    flash(f"Removed {title} from favorites.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug, use_reloader=debug, host="0.0.0.0", port=port)
