# build_model.py — run once to generate model/movie_list.pkl and model/similarity.pkl
# Streamlit Cloud will NOT run this automatically; see README for instructions.

import ast
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build():
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')

    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    movies.dropna(inplace=True)

    def convert(text):
        return [i['name'] for i in ast.literal_eval(text)]

    def fetch_director(text):
        return [i['name'] for i in ast.literal_eval(text) if i['job'] == 'Director']

    def collapse(L):
        return [i.replace(' ', '') for i in L]

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(convert).apply(lambda x: x[:3])
    movies['crew'] = movies['crew'].apply(fetch_director)

    for col in ['cast', 'crew', 'genres', 'keywords']:
        movies[col] = movies[col].apply(collapse)

    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    movies['tags'] = (
        movies['overview'] + movies['genres'] +
        movies['keywords'] + movies['cast'] + movies['crew']
    )

    new = movies.drop(columns=['overview', 'genres', 'keywords', 'cast', 'crew'])
    new['tags'] = new['tags'].apply(lambda x: ' '.join(x))

    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector = cv.fit_transform(new['tags']).toarray()
    similarity = cosine_similarity(vector)

    os.makedirs('model', exist_ok=True)
    pickle.dump(new, open('model/movie_list.pkl', 'wb'))
    pickle.dump(similarity, open('model/similarity.pkl', 'wb'))
    print(f"Model built: {len(new)} movies, similarity matrix {similarity.shape}")


if __name__ == '__main__':
    build()
