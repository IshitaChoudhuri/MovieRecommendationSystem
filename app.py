import pickle
import pandas as pd
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def set_up_retry_strategy(session):
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

# Function to fetch movie poster
def fetch_poster(movie_id):
    with requests.Session() as session:
        set_up_retry_strategy(session)

        url = "https://api.themoviedb.org/3/movie/{}?api_key=379b584b07d7eb144abd3279d132faa9&language=en-US".format(movie_id)
        try:
            response = session.get(url)
            response.raise_for_status() # Raise an error for bad responses
            data = response.json()

            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w185/" + poster_path
            else:
                st.warning("Poster not available for this movie.")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching poster: {e}")
            return None


# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    for i in movies_list:
        # Fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movie_posters

# Load data
movies_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('sim.pkl', 'rb'))

# Set page title and favicon
st.set_page_config(page_title='Movie Recommender System', page_icon='🎬', layout='wide')

# Custom CSS styling
st.markdown(
    """
    <style>
        body {
            background-color: #f4f4f4;
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .stButton {
            color: #fff;
            background-color: #ff5e00;
            border-radius: 5px;
            padding: 8px 12px;
            font-size: 16px;
        }
        .stButton:hover {
            background-color: #ff814a;
        }
        .stImage {
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add some styling
st.title('🍿 Movie Recommender System')

# Dropdown for user input
selected_movie_name = st.selectbox('Select a Movie', movies['title'].values)

if st.button('Get Recommendations', key='recommend_button'):
    names, posters = recommend(selected_movie_name)

    # Display recommendations in a grid layout
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        if posters[0] is not None:
            st.image(posters[0], use_column_width=True)

    with col2:
        st.text(names[1])
        if posters[1] is not None:
            st.image(posters[1], use_column_width=True)

    with col3:
        st.text(names[2])
        if posters[2] is not None:
            st.image(posters[2], use_column_width=True)

    with col4:
        st.text(names[3])
        if posters[3] is not None:
            st.image(posters[3], use_column_width=True)

    with col5:
        st.text(names[4])
        if posters[4] is not None:
            st.image(posters[4], use_column_width=True)
