from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

movies = joblib.load("movies.pkl")
similarity = joblib.load("similarity.pkl")

poster_data = pd.read_csv("datasets/tmdb_5000_movies.csv")

poster_lookup = {}

if "id" in poster_data.columns and "poster_path" in poster_data.columns:
    poster_lookup = dict(zip(poster_data["id"], poster_data["poster_path"]))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    movie_name = data.get("movie", "").strip()

    if not movie_name:
        return jsonify({"error": "Please enter a movie title."}), 400

    matches = movies[movies["title"].str.lower() == movie_name.lower()]

    if matches.empty:
        return jsonify({"error": "Movie not found. Try another title."}), 404

    movie_index = matches.index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        enumerate(distances),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommendations = []

    for index, score in movie_list:
        movie = movies.iloc[index]
        movie_id = int(movie["id"])

        poster_path = poster_lookup.get(movie_id)

        poster_url = None

        if isinstance(poster_path, str) and poster_path.startswith("/"):
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

        recommendations.append({
            "title": movie["title"],
            "similarity": round(float(score) * 100, 2),
            "poster": poster_url
        })

    return jsonify({
        "movie": movie_name,
        "recommendations": recommendations
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)