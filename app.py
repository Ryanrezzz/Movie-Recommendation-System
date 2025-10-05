import streamlit as st
import pickle


movies_list=pickle.load(open('movies.pkl','rb'))

movie_list_array=movies_list['title'].values
similarity=pickle.load(open('similarity.pkl','rb'))
def recommend(movie):
    # Find the index by matching the title column explicitly
    movie_index=movies_list[movies_list['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list1=sorted(list(enumerate(distances)),reverse=True,key=lambda x: x[1])[1:6]
    recommnded_movies=[]
    for i in movies_list1:
        recommnded_movies.append(movies_list['title'][i[0]])
    return recommnded_movies



st.title('Movie Recommender System')
selected_movie_name = st.selectbox(
    "What movie you would like to choose?",
    movie_list_array,
)
if st.button("Recommend"):
    recommendation=recommend(selected_movie_name)
    for i in recommendation:
       st.write(i)
