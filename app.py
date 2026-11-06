from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

movies = joblib.load("movies_combined.pkl")
vectors = joblib.load("vectors_combined.pkl")

tmdb = pd.read_csv("datasets/tmdb_5000_movies.csv")

poster_lookup = {}

if "id" in tmdb.columns and "poster_path" in tmdb.columns:
    poster_lookup = dict(zip(tmdb["id"], tmdb["poster_path"]))

genre_lookup = {}

if "id" in tmdb.columns and "genres" in tmdb.columns:
    for _, row in tmdb.iterrows():
        try:
            import ast
            genre_lookup["tmdb_" + str(row["id"])] = [
                item["name"]
                for item in ast.literal_eval(row["genres"])
            ]
        except:
            genre_lookup["tmdb_" + str(row["id"])] = []

indian = pd.read_csv("datasets/indian_movies.csv")

indian_genres = {}

for _, row in indian.iterrows():
    try:
        indian_genres["imdb_" + str(row["ID"])] = [
            x.strip() for x in str(row["Genre"]).split(",")
            if x.strip() and x.strip() != "-"
        ]
    except:
        pass


@app.route("/")
def home():
    languages = sorted(
        movies[movies["industry"] == "Indian"]["language"]
        .dropna().unique().tolist()
    )

    genres = sorted({
        genre
        for genre_list in list(genre_lookup.values()) + list(indian_genres.values())
        for genre in genre_list
    })

    return render_template(
        "index.html",
        languages=languages,
        genres=genres
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}

    movie_name = data.get("movie", "").strip()
    industry = data.get("industry", "All")
    language = data.get("language", "All")
    genre = data.get("genre", "All")

    if not movie_name:
        return jsonify({"error": "Please enter a movie title."}), 400

    matches = movies[
        movies["title"].str.lower() == movie_name.lower()
    ]

    if matches.empty:
        return jsonify({"error": "Movie not found. Try another title."}), 404

    movie_index = matches.index[0]

    scores = cosine_similarity(
        vectors[movie_index],
        vectors
    ).flatten()

    candidates = movies.copy()
    candidates["score"] = scores

    candidates = candidates.drop(index=movie_index)

    if industry != "All":
        candidates = candidates[
            candidates["industry"] == industry
        ]

    if language != "All":
        candidates = candidates[
            candidates["language"].str.lower() == language.lower()
        ]

    if genre != "All":
        candidates = candidates[
            candidates["id"].apply(
                lambda x: genre in (
                    genre_lookup.get(x, [])
                    if str(x).startswith("tmdb_")
                    else indian_genres.get(x, [])
                )
            )
        ]

    candidates = candidates.sort_values(
        "score",
        ascending=False
    ).head(10)

    recommendations = []

    for _, row in candidates.iterrows():
        movie_id = row["id"]
        poster = None

        if str(movie_id).startswith("tmdb_"):
            tmdb_id = int(str(movie_id).replace("tmdb_", ""))
            poster_path = poster_lookup.get(tmdb_id)

            if isinstance(poster_path, str) and poster_path.startswith("/"):
                poster = "https://image.tmdb.org/t/p/w500" + poster_path

        movie_genres = (
            genre_lookup.get(movie_id, [])
            if str(movie_id).startswith("tmdb_")
            else indian_genres.get(movie_id, [])
        )

        recommendations.append({
            "title": row["title"],
            "poster": poster,
            "industry": row["industry"],
            "language": row["language"],
            "genres": movie_genres,
            "similarity": round(float(row["score"]) * 100, 2)
        })

    return jsonify({
        "movie": movie_name,
        "recommendations": recommendations
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)