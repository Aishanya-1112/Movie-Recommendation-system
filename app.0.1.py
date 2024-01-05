import streamlit as st
import pickle
import requests


movies = pickle.load(open("movie_list.pkl","rb"))
movies_list = movies['title'].values
st.header("Movie Recomender")
selected_value = st.selectbox("Select the Movie you previously liked",movies_list)



#fetchng poster 
def f_poster(movie_id):
    url ="https://api.themoviedb.org/3/movie/{}?api_key=dec4731f59413ae816d86ea96c1b1677&language=en-US".format(movie_id)
    data=requests.get(url)
    data=data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
    return full_path

# movie  pass this into function in final iteration
def fucn():
    r_movie =[] 
    r_poster=[]
    #for i in movies[1:5]:
    #    r_movie.append(movies.iloc[i[0]].title)
    top_5_array = movies['title'].head(5).tolist()
    top_5_poster = movies['id'].head(5).tolist()
    #    r_movie.append(movies.iloc[i[0]].title)
    for i in top_5_poster:
        r_poster.append(f_poster(i))

    return top_5_array,r_poster


if st.button("Show Recommendations"):
    # selected_value  pass this into function in final iteration
    mov_name, mov_pos= fucn()
    col1,col2,col3,col4,col5 =st.columns(5)

    with col1:
        st.text(mov_name[0])
        st.image(mov_pos[0])
    with col2:
        st.text(mov_name[1])
        st.image(mov_pos[1])
    with col3:
        st.text(mov_name[2])
        st.image(mov_pos[2])
    with col4:
        st.text(mov_name[3])
        st.image(mov_pos[3])
    with col5:
        st.text(mov_name[4])
        st.image(mov_pos[4])