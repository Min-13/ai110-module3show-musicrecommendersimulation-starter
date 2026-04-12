import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

import csv


# ---------------------------------------------------------------------------
# Hybrid scoring constants
# ---------------------------------------------------------------------------

ALPHA = 0.6   # weight for rule-based score
BETA  = 0.4   # weight for similarity score

# Finalized weights: genre(2.0) + mood(1.0) + acoustic(1.0) = 4.0
_MAX_RULE_RAW = 4.0

# Four numeric features each in [0, 1] → worst-case distance = √4 = 2.0
_MAX_NUMERIC_DIST = math.sqrt(4)

# Songs within ±0.15 of the energy target score 1.0; penalty kicks in beyond.
_ENERGY_TOLERANCE = 0.15

# Small additive bonus for songs released at or after the user's preferred era.
_RECENCY_BONUS = 0.05

# Infer a valence target from the user's stated mood — covers original and
# expanded moods added in the dataset.
_MOOD_TO_VALENCE: Dict[str, float] = {
    "happy":       0.80,
    "chill":       0.62,
    "intense":     0.50,
    "relaxed":     0.70,
    "focused":     0.59,
    "moody":       0.49,
    "energetic":   0.72,
    "romantic":    0.78,
    "peaceful":    0.65,
    "angry":       0.30,
    "nostalgic":   0.63,
    "melancholic": 0.32,
    "uplifting":   0.90,
    "dreamy":      0.74,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    The four fields added in the expanded dataset (instrumentalness,
    speechiness, popularity, year) default to safe values so that existing
    tests that construct Song without them continue to pass.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    popularity: int = 50
    year: int = 2020


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    The three new fields default to neutral values so that existing tests
    that construct UserProfile without them continue to pass.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    wants_instrumental: bool = False   # True → prefers tracks with few/no vocals
    preferred_era: int = 2000          # songs from this year onward get a small bonus
    min_popularity: int = 0            # songs below this threshold are filtered out


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _energy_gap(song_energy: float, target: float) -> float:
    """Return 0.0 inside the ±ENERGY_TOLERANCE band, the raw overshoot beyond it."""
    return max(0.0, abs(song_energy - target) - _ENERGY_TOLERANCE)


def _rule_score(song: Song, user: UserProfile) -> float:
    """Award points for genre (+2.0), mood (+1.0), and acoustic (+1.0) matches, normalised to [0, 1]."""
    raw = 0.0
    if song.genre == user.favorite_genre:
        raw += 2.0
    if song.mood == user.favorite_mood:
        raw += 1.0
    if user.likes_acoustic and song.acousticness > 0.6:
        raw += 1.0
    return raw / _MAX_RULE_RAW


def _similarity_score(song: Song, user: UserProfile) -> float:
    """Return 1 - normalised Euclidean distance across energy, acousticness, valence, and instrumentalness."""
    target_acousticness    = 0.75 if user.likes_acoustic    else 0.15
    target_instrumentalness = 0.75 if user.wants_instrumental else 0.20
    target_valence         = _MOOD_TO_VALENCE.get(user.favorite_mood, 0.60)

    distance = math.sqrt(
        _energy_gap(song.energy, user.target_energy)          ** 2 +
        (song.acousticness     - target_acousticness)         ** 2 +
        (song.valence          - target_valence)              ** 2 +
        (song.instrumentalness - target_instrumentalness)     ** 2
    )
    return 1.0 - (distance / _MAX_NUMERIC_DIST)


def _hybrid_score(song: Song, user: UserProfile) -> float:
    """Combine rule and similarity scores (60/40) with an optional recency bonus, capped at 1.0."""
    base = ALPHA * _rule_score(song, user) + BETA * _similarity_score(song, user)
    recency_bonus = _RECENCY_BONUS if song.year >= user.preferred_era else 0.0
    return min(1.0, base + recency_bonus)


def _build_explanation(song: Song, user: UserProfile) -> str:
    """Return a semicolon-joined string of reasons explaining why this song scored as it did."""
    reasons = []

    # Rule layer
    if song.genre == user.favorite_genre:
        reasons.append(f"genre matched ({song.genre})")
    if song.mood == user.favorite_mood:
        reasons.append(f"mood matched ({song.mood})")
    if user.likes_acoustic and song.acousticness > 0.6:
        reasons.append(f"acoustic feel matched (acousticness {song.acousticness:.2f})")

    # Similarity layer — energy (tolerance band)
    gap = abs(song.energy - user.target_energy)
    if gap <= _ENERGY_TOLERANCE:
        reasons.append(
            f"energy within target range ({song.energy:.2f} vs target {user.target_energy:.2f})"
        )
    else:
        reasons.append(
            f"energy outside target range ({song.energy:.2f} vs target {user.target_energy:.2f})"
        )

    # Similarity layer — instrumentalness
    if user.wants_instrumental:
        if song.instrumentalness >= 0.60:
            reasons.append(f"instrumental preference matched ({song.instrumentalness:.2f})")
        elif song.instrumentalness < 0.40:
            reasons.append(f"has noticeable vocals (instrumentalness {song.instrumentalness:.2f})")

    # Recency bonus
    if song.year >= user.preferred_era:
        reasons.append(f"released in preferred era ({song.year})")

    if not reasons:
        return "Low overall match — no strong feature alignment found."
    return "Because: " + "; ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Public scoring function
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user_prefs using the hybrid recipe; return (score, reasons)."""
    reasons: List[str] = []
    rule_raw = 0.0

    # --- Rule layer: categorical matches ---
    if song.get("genre") == user_prefs.get("genre"):
        rule_raw += 2.0
        reasons.append(f"genre match (+2.0)")

    if song.get("mood") == user_prefs.get("mood"):
        rule_raw += 1.0
        reasons.append(f"mood match (+1.0)")

    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
    if likes_acoustic and float(song.get("acousticness", 0)) > 0.6:
        rule_raw += 1.0
        reasons.append(f"acoustic preference match (+1.0)")

    rule_score = rule_raw / _MAX_RULE_RAW

    # --- Similarity layer: numeric proximity ---
    target_energy          = float(user_prefs.get("energy", 0.5))
    target_acousticness    = 0.75 if likes_acoustic else 0.15
    target_valence         = _MOOD_TO_VALENCE.get(str(user_prefs.get("mood", "")), 0.60)
    wants_instrumental     = bool(user_prefs.get("wants_instrumental", False))
    target_instrumentalness = 0.75 if wants_instrumental else 0.20

    song_energy          = float(song.get("energy", 0))
    song_acousticness    = float(song.get("acousticness", 0))
    song_valence         = float(song.get("valence", 0))
    song_instrumentalness = float(song.get("instrumentalness", 0))

    energy_component = _energy_gap(song_energy, target_energy)
    distance = math.sqrt(
        energy_component                              ** 2 +
        (song_acousticness    - target_acousticness)  ** 2 +
        (song_valence         - target_valence)       ** 2 +
        (song_instrumentalness - target_instrumentalness) ** 2
    )
    sim_score = 1.0 - (distance / _MAX_NUMERIC_DIST)

    energy_gap_val = abs(song_energy - target_energy)
    if energy_gap_val <= _ENERGY_TOLERANCE:
        reasons.append(
            f"energy within target range ({song_energy:.2f} vs {target_energy:.2f}, +{sim_score:.2f} similarity)"
        )
    else:
        reasons.append(
            f"energy outside target range ({song_energy:.2f} vs {target_energy:.2f}, +{sim_score:.2f} similarity)"
        )

    if wants_instrumental:
        if song_instrumentalness >= 0.6:
            reasons.append(f"instrumental match ({song_instrumentalness:.2f})")
        else:
            reasons.append(f"has vocals ({song_instrumentalness:.2f})")

    # --- Hybrid score ---
    base = ALPHA * rule_score + BETA * sim_score

    # --- Recency bonus ---
    preferred_era = int(user_prefs.get("preferred_era", 2000))
    song_year = int(song.get("year", 0))
    if song_year >= preferred_era:
        base += _RECENCY_BONUS
        reasons.append(f"released in preferred era ({song_year}, +{_RECENCY_BONUS})")

    final_score = min(1.0, base)
    return final_score, reasons


# ---------------------------------------------------------------------------
# OOP interface  (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Filter by min_popularity, rank the remainder by hybrid score,
        return top-k.
        """
        pool = [s for s in self.songs if s.popularity >= user.min_popularity]
        ranked = sorted(pool, key=lambda s: _hybrid_score(s, user), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation for why song was recommended."""
        return _build_explanation(song, user)


# ---------------------------------------------------------------------------
# Functional interface  (required by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numerics cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "speechiness":      float(row["speechiness"]),
                "popularity":       int(row["popularity"]),
                "year":             int(row["year"]),
            })
    return songs


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """Filter by popularity, score every song with score_song, return top-k sorted highest first."""
    min_popularity = int(user_prefs.get("min_popularity", 0))

    # Step 1 — filter: list comprehension removes songs below the popularity floor
    pool = [s for s in songs if int(s.get("popularity", 0)) >= min_popularity]

    # Step 2 — judge: list comprehension calls score_song on every song in the pool
    scored = [
        (song, score, "; ".join(reasons))
        for song in pool
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # Step 3 — rank: sorted() returns a new list (original untouched), [:k] slices top results
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
