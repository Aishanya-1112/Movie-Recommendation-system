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

# Load movie and course data
movies = pd.read_csv(r"top10K-TMDB-movies.csv")
courses = pd.read_csv(r"Coursera.csv")

def get_movie_recommendations(movie_title, previous_movies):
    df_excluded = movies[(~movies['title'].isin(previous_movies)) & (movies['title'] != movie_title)]
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_excluded['overview'].fillna(''))
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_vectorizer.transform([movies[movies['title'] == movie_title]['overview'].iloc[0]]))
    similar_movies_indices = cosine_similarities.flatten().argsort()[::-1]
    similar_movies = df_excluded.iloc[similar_movies_indices]['title'].head(5).tolist()
    posters = [fetch_poster(movie) for movie in similar_movies]
    return similar_movies, posters

def get_course_recommendations(course_name, difficulty_level, previous_courses):
    df_excluded = courses[
        (~courses['Course Name'].isin(previous_courses)) &
        (courses['Course Name'] != course_name) &
        (courses['Difficulty Level'] == difficulty_level)
    ]
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_excluded['Course Description'].fillna(''))
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_vectorizer.transform([courses[courses['Course Name'] == course_name]['Course Description'].iloc[0]]))
    similar_courses_indices = cosine_similarities.flatten().argsort()[::-1]
    similar_courses = df_excluded.iloc[similar_courses_indices].head(5)
    return similar_courses

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

def get_course_details(course_name):
    course_details = courses[courses['Course Name'] == course_name].to_dict(orient='records')[0]
    return course_details


def get_movie_recommendations_app():
    st.header("Movie Recommender")
    selected_value = st.selectbox("Select the Movie you previously liked", movies['title'].values)

    if st.button("Show Recommendations"):
        recommendations, posters = get_movie_recommendations(selected_value, [])
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


def get_course_recommendations_app():
    st.header("Course Recommender")
    selected_value = st.selectbox("Select the Course you previously liked", courses['Course Name'].values)
    difficulty_level = st.selectbox("Select the Difficulty Level", courses['Difficulty Level'].unique())

    if st.button("Show Recommendations"):
        recommendations = get_course_recommendations(selected_value, difficulty_level, [])
        for index, row in recommendations.iterrows():
            # Use HTML styling to highlight the course name with a black background and capitalize it
            st.markdown(f'<div style="background-color: black; padding: 10px; text-align: center; text-transform: uppercase;">{row["Course Name"]}</div>', unsafe_allow_html=True)

            st.write(f"University: {row['University']}")
            st.write(f"Difficulty Level: {row['Difficulty Level']}")
            st.write(f"Course Rating: {row['Course Rating']}")
            st.write(f"Skills: {row['Skills']}")
            st.write(f"Course URL: {row['Course URL']}")
            with st.expander(f"Overview for {row['Course Name']}"):
                course_details = get_course_details(row['Course Name'])
                st.subheader("Overview:")
                st.write(course_details['Course Description'])



# Main Streamlit app
st.title(" Recommendation System ")

# Dropdown selector for Movies and Courses
option = st.selectbox("Choose an option:", ("Movies", "Courses"))

if option == "Movies":
    get_movie_recommendations_app()
elif option == "Courses":
    get_course_recommendations_app()