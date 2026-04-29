from flask import Flask, flash, redirect, render_template, request, session, url_for
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

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "vibetune-secret-dev-key-change-in-prod")

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
    preferred = get_language_config(user)["country"]
    return list(dict.fromkeys([preferred, "IN", "US", "GB"]))


def normalize_itunes_track(track, country):
    title = track.get("trackName") or "Unknown Title"
    artist = track.get("artistName") or "Unknown Artist"
    album = track.get("collectionName") or "Single"
    genre = track.get("primaryGenreName") or "Music"
    return {
        "title": title,
        "artist": artist,
        "language": "Music",
        "genre": genre,
        "album": album,
        "website_url": build_apple_music_search_url(title, artist, country),
        "app_url": "",
        "play_url": build_apple_music_search_url(title, artist, country),
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
    website_url = (song.get("website_url") or song.get("play_url") or "").strip()
    if not website_url:
        website_url = build_apple_music_search_url(title, artist, "us")

    return {
        "title": title,
        "artist": artist,
        "language": song.get("language", "Music"),
        "genre": song.get("genre", song.get("album", "Single")),
        "album": song.get("album", "Single"),
        "website_url": website_url,
        "app_url": "",
        "play_url": website_url,
        "track_id": song.get("track_id", ""),
    }


def get_conversation():
    conversation = session.get("conversation", [])
    return conversation if isinstance(conversation, list) else []


@app.route("/")
def index():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    normalized_user = dict(user)
    normalized_user["favorites"] = [normalize_track(song) for song in user.get("favorites", [])]

    conversation = get_conversation()
    query = session.get("last_query", "")
    has_more = session.get("has_more_recommendations", False)
    return render_template(
        "index.html",
        user=normalized_user,
        conversation=conversation,
        last_query=query,
        has_more=has_more,
    )


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
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


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
    saved_user["genre"] = request.form.get("genre", "Pop").strip() or "Pop"
    save_users(users)
    flash("Preferences updated.", "success")
    return redirect(url_for("index"))


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
        session["conversation"] = conversation
        session["last_query"] = query
        session["has_more_recommendations"] = False
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
        session["conversation"] = conversation
        session["last_query"] = query
        session["has_more_recommendations"] = False
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
        session["conversation"] = conversation
        session["last_query"] = query
        session["has_more_recommendations"] = False
        return redirect(url_for("index"))

    picks, has_more = paginate_recommendations(pool, offset=0, count=recommendation_count)
    session["recommendation_pool"] = [normalize_track(song) for song in pool]
    session["last_mood"] = mood
    session["last_query"] = query
    session["last_song_intent"] = song_intent
    session["last_recommendation_count"] = recommendation_count
    session["recommendation_offset"] = 0
    session["has_more_recommendations"] = has_more

    turn = {
        "query": query,
        "assistant_message": (
            (
                f'I found "{reference_song["title"]}" by {reference_song["artist"]} first. '
                if reference_song else ""
            )
            + f"{build_recommendation_intro(mood, user)} "
            f"I found {min(recommendation_count, len(pool))} Apple Music songs based on your request."
        ),
        "reference_song": normalize_track(reference_song) if reference_song else None,
        "recommendations": [normalize_track(song) for song in picks],
    }
    conversation.append(turn)
    session["conversation"] = conversation
    return redirect(url_for("index"))


@app.route("/recommend/more", methods=["POST"])
def recommend_more():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    query = session.get("last_query", "").strip()
    if not query:
        flash("Ask for songs first, then use More songs.", "error")
        return redirect(url_for("index"))

    recommendation_count = session.get("last_recommendation_count") or get_recommendation_count(query)
    next_offset = session.get("recommendation_offset", 0) + recommendation_count
    pool = session.get("recommendation_pool", [])
    mood = session.get("last_mood", detect_mood(query))
    picks, has_more = paginate_recommendations(pool, offset=next_offset, count=recommendation_count)
    if not picks:
        flash("I’ve reached the end of the current Apple Music batch. Try a more detailed mood or a different genre for fresh results.", "error")
        session["has_more_recommendations"] = False
        return redirect(url_for("index"))

    session["last_mood"] = mood
    session["recommendation_offset"] = next_offset
    session["has_more_recommendations"] = has_more

    conversation = get_conversation()
    if conversation:
        latest_turn = conversation[-1]
        existing = latest_turn.get("recommendations", [])
        existing.extend([normalize_track(song) for song in picks])
        latest_turn["recommendations"] = existing
        conversation[-1] = latest_turn
        session["conversation"] = conversation

    flash(f"Here are {len(picks)} more Apple Music songs for the same mood.", "success")
    return redirect(url_for("index"))


@app.route("/conversation/clear", methods=["POST"])
def clear_conversation():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    session["conversation"] = []
    session["recommendation_pool"] = []
    session["recommendation_offset"] = 0
    session["has_more_recommendations"] = False
    session["last_query"] = ""
    session["last_mood"] = ""
    session["reference_song"] = None
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
    app.run(debug=debug, use_reloader=debug, host="127.0.0.1", port=port)
