import pandas as pd
import ast
import joblib
from sklearn.feature_extraction.text import CountVectorizer

print("Loading datasets...")

movies = pd.read_csv("datasets/tmdb_5000_movies.csv")
credits = pd.read_csv("datasets/tmdb_5000_credits.csv")
indian = pd.read_csv("datasets/indian_movies.csv")

def parse_names(value):
    try:
        return [x["name"].replace(" ", "") for x in ast.literal_eval(value)]
    except:
        return []

def get_director(value):
    try:
        for item in ast.literal_eval(value):
            if item.get("job") == "Director":
                return [item["name"].replace(" ", "")]
    except:
        pass
    return []

print("Preparing international movies...")

tmdb = movies.merge(credits, left_on="id", right_on="movie_id")
tmdb = tmdb[["id", "title_x", "overview", "genres", "keywords", "cast", "crew"]].copy()

tmdb["overview"] = tmdb["overview"].fillna("")
tmdb["genres"] = tmdb["genres"].apply(parse_names)
tmdb["keywords"] = tmdb["keywords"].apply(parse_names)
tmdb["cast"] = tmdb["cast"].apply(lambda x: parse_names(x)[:3])
tmdb["crew"] = tmdb["crew"].apply(get_director)
tmdb["overview"] = tmdb["overview"].apply(str.split)

tmdb["tags"] = (
    tmdb["overview"] + tmdb["genres"] +
    tmdb["keywords"] + tmdb["cast"] + tmdb["crew"]
)

international = pd.DataFrame({
    "id": "tmdb_" + tmdb["id"].astype(str),
    "title": tmdb["title_x"].astype(str),
    "tags": tmdb["tags"].apply(lambda x: " ".join(x).lower()),
    "industry": "International",
    "language": "Unknown",
    "year": ""
})

print("Preparing Indian movies...")

for col in ["Genre", "Language", "Year"]:
    indian[col] = indian[col].fillna("").astype(str)

indian_movies = pd.DataFrame({
    "id": "imdb_" + indian["ID"].astype(str),
    "title": indian["Movie Name"].astype(str),
    "tags": (
        indian["Movie Name"] + " " +
        indian["Genre"] + " " +
        indian["Language"] + " " +
        indian["Year"]
    ).str.lower(),
    "industry": "Indian",
    "language": indian["Language"].str.lower(),
    "year": indian["Year"]
})

print("Combining datasets...")

combined = pd.concat([international, indian_movies], ignore_index=True)
combined.drop_duplicates(subset="id", inplace=True)
combined.reset_index(drop=True, inplace=True)

print("Total movies:", len(combined))

cv = CountVectorizer(max_features=10000, stop_words="english")
vectors = cv.fit_transform(combined["tags"])

joblib.dump(combined, "movies_combined.pkl")
joblib.dump(vectors, "vectors_combined.pkl")
joblib.dump(cv, "vectorizer_combined.pkl")

print("Combined model saved successfully!")
print("Vector shape:", vectors.shape)
import pandas as pd
import ast
import joblib
from sklearn.feature_extraction.text import CountVectorizer

print("Loading datasets...")

movies = pd.read_csv("datasets/tmdb_5000_movies.csv")
credits = pd.read_csv("datasets/tmdb_5000_credits.csv")
indian = pd.read_csv("datasets/indian_movies.csv")

def parse_names(value):
    try:
        return [x["name"].replace(" ", "") for x in ast.literal_eval(value)]
    except (ValueError, TypeError, SyntaxError):
        return []

def get_cast(value):
    return parse_names(value)[:3]

def get_director(value):
    try:
        for item in ast.literal_eval(value):
            if item.get("job") == "Director":
                return [item["name"].replace(" ", "")]
    except (ValueError, TypeError, SyntaxError):
        pass
    return []

print("Preparing international movies...")

tmdb = movies.merge(credits, left_on="id", right_on="movie_id")
tmdb = tmdb[["id", "title_x", "overview", "genres", "keywords", "cast", "crew"]].copy()
tmdb.rename(columns={"title_x": "title"}, inplace=True)

tmdb["overview"] = tmdb["overview"].fillna("").astype(str)
tmdb["genres"] = tmdb["genres"].apply(parse_names)
tmdb["keywords"] = tmdb["keywords"].apply(parse_names)
tmdb["cast"] = tmdb["cast"].apply(get_cast)
tmdb["crew"] = tmdb["crew"].apply(get_director)
tmdb["overview"] = tmdb["overview"].apply(str.split)

tmdb["tags"] = (
    tmdb["overview"] + tmdb["genres"] +
    tmdb["keywords"] + tmdb["cast"] + tmdb["crew"]
)

international = pd.DataFrame({
    "id": "tmdb_" + tmdb["id"].astype(str),
    "title": tmdb["title"].astype(str),
    "tags": tmdb["tags"].apply(lambda x: " ".join(x).lower()),
    "industry": "International",
    "language": "Unknown",
    "year": ""
})

print("Preparing Indian movies...")

indian["Genre"] = indian["Genre"].fillna("").astype(str)
indian["Language"] = indian["Language"].fillna("Unknown").astype(str)
indian["Year"] = indian["Year"].fillna("").astype(str)

indian_movies = pd.DataFrame({
    "id": "imdb_" + indian["ID"].astype(str),
    "title": indian["Movie Name"].astype(str),
    "tags": (
        indian["Movie Name"] + " " +
        indian["Genre"] + " " +
        indian["Language"] + " " +
        indian["Year"]
    ).str.lower(),
    "industry": "Indian",
    "language": indian["Language"].str.lower(),
    "year": indian["Year"]
})

print("Combining datasets...")

combined = pd.concat([international, indian_movies], ignore_index=True)
combined.drop_duplicates(subset="id", inplace=True)
combined.reset_index(drop=True, inplace=True)

print("Total movies:", len(combined))
print("Creating recommendation vectors...")

cv = CountVectorizer(max_features=10000, stop_words="english")
vectors = cv.fit_transform(combined["tags"])

joblib.dump(combined, "movies_combined.pkl")
joblib.dump(vectors, "vectors_combined.pkl")
joblib.dump(cv, "vectorizer_combined.pkl")

print("\nCombined model saved successfully!")
print("Vector shape:", vectors.shape)
print("Original model files remain unchanged.")
