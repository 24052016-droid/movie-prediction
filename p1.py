import pandas as pd 
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
movies=pd.read_csv("datasets/tmdb_5000_movies.csv")
credits=pd.read_csv("datasets/tmdb_5000_credits.csv")
print("movies shape:",movies.shape)
print("credits shape:",credits.shape)
print(movies.head())
#merging 
movies=movies.merge(credits,left_on="id",right_on="movie_id")
print("merged shape :",movies.shape)
print(movies.head())
#missing 
print("missing values :")
print(movies.isnull().sum())
print("dulpicate values:")
print(movies.duplicated().sum())
print("columns")
print(movies.columns.to_list())
#rename
movies=movies[["movie_id","title_x","overview","genres","keywords","cast","crew"]]
movies.rename(columns={"movie_id":"id","title_x":"title"},inplace=True)
#handle
movies['overview']=movies['overview'].fillna('')
#removing
movies.drop_duplicates(inplace=True)
print(movies.head())
print("final shape:",movies.shape)
#conv string to obj 
data='[{"id":28,"name":"Actions"}]'
print(ast.literal_eval(data))
def convert(obj):
    L=[]
    for i in ast.literal_eval(obj):
        L.append(i["name"])
    return L
movies["genres"]=movies['genres'].apply(convert)
movies["keywords"]=movies["keywords"].apply(convert)
print(movies[['title','genres','keywords']].head())
# top 3
def convert3(obj):
    L=[]
    counter =0
    for i in ast.literal_eval(obj):
        if counter<3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

movies['cast'] = movies['cast'].apply(convert3)
# director
def fetch_director(obj):
    L = []

    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L
movies['crew'] = movies['crew'].apply(fetch_director)
# Remove spaces from names
movies['cast'] = movies['cast'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['crew'] = movies['crew'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['genres'] = movies['genres'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['keywords'] = movies['keywords'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)


# Convert overview into a list of words
movies['overview'] = movies['overview'].apply(
    lambda x: x.split()
)


# Combine all features
movies['tags'] = (
    movies['overview'] +
    movies['genres'] +
    movies['keywords'] +
    movies['cast'] +
    movies['crew']
)
# Create a new dataframe
new_df = movies[['id', 'title', 'tags']].copy()
new_df['tags'] = new_df['tags'].apply(
    lambda x: " ".join(x))
# Convert everything to lowercase
new_df['tags'] = new_df['tags'].apply(
    lambda x: x.lower())
print(new_df.head())
#text to vector
cv = CountVectorizer(
    max_features=5000,
    stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
print("Vector shape:", vectors.shape)
similarity = cosine_similarity(vectors)
print("Similarity matrix shape:", similarity.shape)
def recommend(movie):

    movie = movie.lower()

    movie_index = new_df[
        new_df['title'].str.lower() == movie
    ].index

    if len(movie_index) == 0:
        print("Movie not found!")
        return

    movie_index = movie_index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        enumerate(distances),
        reverse=True,
        key=lambda x: x[1]
    )

    print("\nRecommended movies:\n")

    for i in movie_list[1:6]:
        print(new_df.iloc[i[0]].title)
recommend("Avatar")
recommend("The Dark Knight")
recommend("Iron Man")
recommend("Titanic")
recommend("Spectre")
joblib.dump(new_df, 'movies.pkl')
joblib.dump(similarity, 'similarity.pkl')
print("Model files saved successfully!")