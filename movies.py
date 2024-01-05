import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url(https://images.pexels.com/photos/1146134/pexels-photo-1146134.jpeg);
    background-size: 180%, cover;
    background-position: top left, center;
    background-repeat: no-repeat;
    background-attachment: local, fixed;
}

h1 {
    text-align: center;
}

.button-container {
    display: flex;
    justify-content: center;
    gap: 20px;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Load movie data
movies = pd.read_csv(r"top10K-TMDB-movies.csv")

def get_movie_recommendations(movie_title, previous_movies):
    df_excluded = movies[(~movies['title'].isin(previous_movies)) & (movies['title'] != movie_title)]
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_excluded['overview'].fillna(''))
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_vectorizer.transform([movies[movies['title'] == movie_title]['overview'].iloc[0]]))
    similar_movies_indices = cosine_similarities.flatten().argsort()[::-1]
    similar_movies = df_excluded.iloc[similar_movies_indices]['title'].head(5).tolist()
    posters = [fetch_poster(movie) for movie in similar_movies]
    return similar_movies, posters

def fetch_poster(movie_title):
    movie_id = movies[movies['title'] == movie_title]['id'].iloc[0]
    url = "https://api.themoviedb.org/3/movie/{}?api_key=dec4731f59413ae816d86ea96c1b1677&language=en-US".format(
        movie_id)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def get_movie_details(movie_title):
    movie_id = movies[movies['title'] == movie_title]['id'].iloc[0]
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=dec4731f59413ae816d86ea96c1b1677&language=en-US"
    data = requests.get(url).json()
    return data

# Streamlit app
def app():
    st.header("Movie Recommender")
    
    # Select a movie the user previously liked
    selected_value = st.selectbox("Select the Movie you previously liked", movies['title'].values)

    # Show Recommendations button
    if st.button("Show Recommendations"):
        recommendations, posters = get_movie_recommendations(selected_value, [])
        
        # Display recommendations and details
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, (recommendation, poster) in enumerate(zip(recommendations, posters)):
            with locals()[f"col{i + 1}"]:
                # Use HTML styling to highlight the movie name with a black background and capitalize it
                st.markdown(f'<div style="background-color: black; padding: 10px; text-align: center; text-transform: uppercase;">{recommendation}</div>', unsafe_allow_html=True)
                st.image(poster)
                with st.expander(f"Overview for {recommendation}"):
                    movie_details = get_movie_details(recommendation)
                    st.subheader("Overview:")
                    st.write(movie_details['overview'])
                    st.subheader("Popularity:")
                    st.write(movie_details['popularity'])
                    st.subheader("Release Date:")
                    st.write(movie_details['release_date'])
                    st.subheader("Rating:")
                    st.write(movie_details['vote_average'])

# Run the Streamlit app
if __name__ == "__main__":
    app()