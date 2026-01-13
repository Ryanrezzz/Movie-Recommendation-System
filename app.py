import streamlit as st
import pickle
import requests
import pandas as pd

# Page config
st.set_page_config(page_title="Multi-Recommendation System", page_icon="🎬", layout="wide")

# OMDb API for Movies
API_KEY = "bc045a9" 
OMDB_URL = "http://www.omdbapi.com/"

# --- Data Loading Functions ---
@st.cache_data
def load_movie_data():
    try:
        movies = pickle.load(open('movies.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading movie data: {e}")
        return None, None

@st.cache_data
def load_book_data():
    try:
        books = pickle.load(open('books_rec.pkl', 'rb'))
        similarity = pickle.load(open('book_similarity.pkl', 'rb'))
        return books, similarity
    except Exception as e:
        st.error(f"Error loading book data: {e}")
        return None, None

@st.cache_data
def load_anime_data():
    try:
        anime = pickle.load(open('anime.pkl', 'rb'))
        similarity = pickle.load(open('compressed_anime.pkl', 'rb'))
        return anime, similarity
    except Exception as e:
        st.error(f"Error loading anime data: {e}")
        return None, None

# --- Helper Functions ---
def fetch_movie_poster(movie_name):
    url = f"{OMDB_URL}?t={movie_name}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "Poster" in data and data["Poster"] != "N/A":
            return data["Poster"]
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# --- Recommendation Functions ---
def recommend_movies(movie, movies, similarity):
    try:
        # Robust index finding
        idx_list = movies[movies['title'] == movie].index
        if len(idx_list) == 0:
            return [], []
        
        index = idx_list[0]
        
        # Check bounds
        if index >= len(similarity):
             st.error(f"Index out of bounds: {index} >= {len(similarity)}")
             return [], []

        distances = similarity[index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_posters = []
        for i in movie_list:
            # Safe access
            if i[0] < len(movies):
                movie_name = movies.iloc[i[0]].title
                recommended_movies.append(movie_name)
                recommended_posters.append(fetch_movie_poster(movie_name))
        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"Error recommending movies: {e}")
        return [], []

def recommend_books(book_name, books, similarity):
    try:
        if book_name not in books['title'].values:
            return [], []
            
        index = books[books['title'] == book_name].index[0]
        distances = similarity[index]
        book_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_books = []
        recommended_images = []
        for i in book_list:
            title = books.iloc[i[0]].title
            recommended_books.append(title)
            
            # Try to get image from 'thumbnail' or 'image' column if it exists
            img_url = "https://via.placeholder.com/300x450?text=No+Image"
            if 'thumbnail' in books.columns:
                 val = books.iloc[i[0]]['thumbnail']
                 if val and isinstance(val, str) and val.startswith('http'):
                     img_url = val
            
            recommended_images.append(img_url)
        return recommended_books, recommended_images
    except Exception as e:
        st.error(f"Error recommending books: {e}")
        return [], []

def recommend_anime(anime_name, anime, similarity):
    try:
        if anime_name not in anime['Name'].values:
            return [], []

        index = anime[anime['Name'] == anime_name].index[0]
        distances = similarity[index]
        anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_anime = []
        recommended_images = []
        for i in anime_list:
            name = anime.iloc[i[0]].Name
            recommended_anime.append(name)
            
            # Try to get image from 'Image URL' column
            img_url = "https://via.placeholder.com/300x450?text=No+Image"
            # Check various common column names for images in anime datasets
            for col in ['Image URL', 'image_url', 'main_picture', 'poster']:
                if col in anime.columns:
                    val = anime.iloc[i[0]][col]
                    if val and isinstance(val, str) and val.startswith('http'):
                        img_url = val
                        break
            
            recommended_images.append(img_url)
        return recommended_anime, recommended_images
    except Exception as e:
        st.error(f"Error recommending anime: {e}")
        return [], []

# --- UI Layout ---
st.markdown("<h1 style='text-align: center;'>NxtWatch🔥</h1>", unsafe_allow_html=True)

# 1. Category Selection
st.markdown("<h3 style='text-align: center; font-family: sans-serif; color: #FF4B4B;'>✨ What are you looking for today? ✨</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1.5, 2, 0.5])
with col2:
    category = st.radio(
        "",
        ("🎬 Movies", "📚 Books", "🎌 Anime"),
        horizontal=True,
    )

st.divider()

# 2. Dynamic Content based on selection
if category == "🎬 Movies":
    movies, similarity_movies = load_movie_data()
    if movies is not None:
        selected_movie = st.selectbox("Select a movie:", movies['title'].values)
        
        if st.button("Recommend Movies", key="btn_movies"):
            with st.spinner('Finding recommendations...'):
                names, posters = recommend_movies(selected_movie, movies, similarity_movies)
                if names:
                    cols = st.columns(5)
                    for i, col in enumerate(cols):
                        if i < len(names):
                            with col:
                                st.image(posters[i], use_container_width=True)
                                st.caption(names[i])
                else:
                    st.warning("No recommendations found.")

elif category == "📚 Books":
    books, similarity_books = load_book_data()
    if books is not None:
        selected_book = st.selectbox("Select a book:", books['title'].values)
        
        if st.button("Recommend Books", key="btn_books"):
            with st.spinner('Finding recommendations...'):
                names, images = recommend_books(selected_book, books, similarity_books)
                if names:
                    cols = st.columns(5)
                    for i, col in enumerate(cols):
                        if i < len(names):
                            with col:
                                st.image(images[i], use_container_width=True)
                                st.caption(names[i])
                else:
                    st.warning("No recommendations found.")

elif category == "🎌 Anime":
    anime, similarity_anime = load_anime_data()
    if anime is not None:
        selected_anime = st.selectbox("Select an anime:", anime['Name'].values)
        
        if st.button("Recommend Anime", key="btn_anime"):
            with st.spinner('Finding recommendations...'):
                names, images = recommend_anime(selected_anime, anime, similarity_anime)
                if names:
                    cols = st.columns(5)
                    for i, col in enumerate(cols):
                        if i < len(names):
                            with col:
                                st.image(images[i], use_container_width=True)
                                st.caption(names[i])
                else:
                    st.warning("No recommendations found.")