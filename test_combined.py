import joblib
from sklearn.metrics.pairwise import cosine_similarity

movies = joblib.load("movies_combined.pkl")
vectors = joblib.load("vectors_combined.pkl")

def recommend(movie_name):
    matches = movies[movies["title"].str.lower() == movie_name.lower()]

    if matches.empty:
        print("Movie not found:", movie_name)
        return

    index = matches.index[0]
    scores = cosine_similarity(vectors[index], vectors).flatten()
    results = scores.argsort()[::-1][1:6]

    print("\nRecommendations for", movie_name)
    for i in results:
        print("-", movies.iloc[i]["title"])

recommend("Avatar")
recommend("The Dark Knight")
recommend("Apna Sapna Money Money")
recommend("Dr. Shaitan")
