"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs



def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile — "late-night creative work" listener
    # Each key maps directly to a field in UserProfile (see recommender.py).
    user_prefs = {
        "genre":              "lofi",  # preferred sonic world: calm, textured, low-key
        "mood":               "focused",  # listening context: deep work, not background noise
        "energy":             0.40,    # target energy: low — nothing distracting
        "likes_acoustic":     True,    # prefers organic textures over synthetic ones
        "wants_instrumental": True,    # no vocals — avoids distraction while working
        "preferred_era":      2020,    # slight preference for recent releases
        "min_popularity":     45,      # filter out very obscure tracks
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 50)
    print("  TOP RECOMMENDATIONS")
    print("=" * 50)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  —  {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}  |  Score: {score:.2f}")
        print(f"    Why:")
        for reason in explanation.split("; "):
            print(f"      • {reason}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
