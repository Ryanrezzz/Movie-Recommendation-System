import streamlit as st
import pickle
import requests

API_KEY = "bc045a9"   # OMDb API key
OMDB_URL = "http://www.omdbapi.com/"

# Load data
movies_list = pickle.load(open('movies.pkl', 'rb'))
movie_list_array = movies_list['title'].values
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch poster from OMDb using movie title
def fetch_poster(movie_name):
    url = f"{OMDB_URL}?t={movie_name}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "Poster" in data and data["Poster"] != "N/A":
        return data["Poster"]
    return None

# Recommend movies
def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list1 = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list1:
        movie_name = movies_list['title'][i[0]]
        recommended_movies.append(movie_name)
        recommended_posters.append(fetch_poster(movie_name))  # poster by title only
    return recommended_movies, recommended_posters

# UI
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "What movie you would like to choose?",
    movie_list_array,
)

if st.button("Recommend"):
    recommendation, posters = recommend(selected_movie_name)

    cols = st.columns(len(recommendation))  # Dynamic number of columns
    for i, col in enumerate(cols):
        with col:
            if posters[i]:
                st.image(posters[i], use_container_width=True)
            st.caption(recommendation[i])