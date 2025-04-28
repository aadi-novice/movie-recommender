# app.py

import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    st.error("API key not found! Please add TMDB_API_KEY to your .env file.")
    st.stop()

# Load your saved movie data
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity

movies_df, similarity = load_data()

# TMDB API to fetch movie posters
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()  # Raise exception for bad responses
        data = data.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except Exception as e:
        st.warning(f"Couldn't fetch poster: {str(e)}")
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()
        return data.json()
    except:
        return None

def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    movie_details = []
    
    for i in movie_list:
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        details = fetch_movie_details(movie_id)
        if details:
            movie_details.append({
                'release_date': details.get('release_date', 'Unknown')[:4] if details.get('release_date') else 'Unknown',
                'rating': round(details.get('vote_average', 0), 1),
                'overview': details.get('overview', 'No description available')
            })
        else:
            movie_details.append({
                'release_date': 'Unknown',
                'rating': 0,
                'overview': 'No description available'
            })
    
    return recommended_movies, recommended_posters, movie_details

# --------------------------- Streamlit UI Starts ---------------------------

# Page configuration
st.set_page_config(
    page_title="Cinematic Compass | Movie Recommendations",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
        /* Main theme */
        [data-testid="stAppViewContainer"] {
            background-color: #0a1929;
            color: #f0f0f0;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #051420;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #64b5f6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Title styling */
        .main-title {
            font-size: 4rem;
            font-weight: 700;
            background: linear-gradient(45deg, #64b5f6, #1e88e5, #0d47a1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
            text-align: center;
            padding: 20px 0 0 0;
        }
        
        .subtitle {
            font-size: 1.5rem;
            color: #bbdefb;
            text-align: center;
            margin-top: 0;
            padding-bottom: 30px;
            font-style: italic;
        }
        
        /* Movie card styling */
        .movie-card {
            background: rgba(13, 71, 161, 0.1);
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(100, 181, 246, 0.2);
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .movie-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(100, 181, 246, 0.5);
        }
        
        .movie-poster {
            border-radius: 10px;
            width: 100%;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        .movie-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #90caf9;
            margin-bottom: 5px;
            text-align: center;
        }
        
        .movie-meta {
            color: #64b5f6;
            font-size: 0.9rem;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .movie-rating {
            background-color: rgba(255, 235, 59, 0.9);
            color: #212121;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            display: inline-block;
        }
        
        .movie-overview {
            font-size: 0.9rem;
            color: #e0e0e0;
            margin-top: 10px;
            flex-grow: 1;
        }
        
        /* Button styling */
        .stButton button {
            background: linear-gradient(45deg, #1976d2, #64b5f6);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 8px 25px;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(25, 118, 210, 0.5);
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background: linear-gradient(45deg, #1565c0, #42a5f5);
            box-shadow: 0 6px 15px rgba(25, 118, 210, 0.7);
            transform: translateY(-2px);
        }
        
        /* Selectbox styling */
        div[data-baseweb="select"] > div {
            background-color: rgba(13, 71, 161, 0.2);
            border: 1px solid #1976d2;
            border-radius: 12px !important;
            color: #bbdefb;
            padding: 5px;
        }
        
        div[data-baseweb="select"] > div:hover {
            border-color: #64b5f6;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            color: #90caf9;
            margin-top: 40px;
            padding: 20px 0 10px 0;
            border-top: 1px solid rgba(100, 181, 246, 0.3);
            font-size: 0.9rem;
        }
        
        /* Card description scrollbar */
        .scrollable-description {
            max-height: 120px;
            overflow-y: auto;
            padding-right: 5px;
        }
        
        .scrollable-description::-webkit-scrollbar {
            width: 4px;
        }
        
        .scrollable-description::-webkit-scrollbar-track {
            background: rgba(13, 71, 161, 0.1);
        }
        
        .scrollable-description::-webkit-scrollbar-thumb {
            background: #1976d2;
            border-radius: 10px;
        }
        
        /* Selected movie highlight */
        .selected-movie {
            background: linear-gradient(90deg, rgba(25, 118, 210, 0.2), rgba(25, 118, 210, 0));
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 4px solid #1976d2;
        }
        
        /* Loading animation */
        .stSpinner > div > div > div > div {
            border-color: #64b5f6 !important;
        }
    </style>
""", unsafe_allow_html=True)
# Add this right after your existing st.markdown CSS section
st.markdown("""
    <style>
        /* Fix dropdown visibility */
        div[data-baseweb="select"] > div {
            background-color: #1565c0 !important;
            border: 2px solid #90caf9 !important;
        }
        
        div[data-baseweb="select"] span {
            color: white !important;
            font-weight: 500;
        }
        
        div[data-baseweb="popover"] {
            background-color: #0a1929 !important;
            border: 1px solid #1976d2 !important;
        }
        
        div[data-baseweb="select"] li {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)
# Add this to your existing CSS section
st.markdown("""
    <style>
        /* Make text visible when typing in the selectbox */
        div[data-baseweb="select"] input {
            color: white !important;
            font-weight: bold !important;
            background-color: transparent !important;
        }
        
        /* Increase contrast for typed text */
        div[data-baseweb="select"] span {
            color: white !important;
            font-weight: bold !important;
        }
        
        /* Add some height to the dropdown */
        div[data-baseweb="select"] > div {
            min-height: 55px !important;
        }
    </style>
""", unsafe_allow_html=True)


# App header
st.markdown('<h1 class="main-title">Cinematic Compass</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover your next favorite film</p>', unsafe_allow_html=True)

# App container
with st.container():
    # Movie selection section
    st.markdown("### 🎬 Start Your Journey")
    st.write("Select a movie you enjoy, and we'll guide you to similar films you might love.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_movie_name = st.selectbox(
            'Choose a movie:',
            options=movies_df['title'].values,
            index=0,
            help="Select a movie you've watched and enjoyed"
        )
    
    with col2:
        recommend_button = st.button('🚀 Find Recommendations')
    
    # Display selected movie info
    if selected_movie_name:
        movie_index = movies_df[movies_df['title'] == selected_movie_name].index[0]
        movie_id = movies_df.iloc[movie_index].movie_id
        poster_url = fetch_poster(movie_id)
        details = fetch_movie_details(movie_id)
        
        st.markdown('<div class="selected-movie">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(poster_url, width=200, caption=None)
        
        with col2:
            st.markdown(f"## {selected_movie_name}")
            if details:
                st.markdown(f"**Release Year:** {details.get('release_date', 'Unknown')[:4] if details.get('release_date') else 'Unknown'}")
                st.markdown(f"**Rating:** {'⭐' * round(details.get('vote_average', 0)/2)} ({details.get('vote_average', 'N/A')})")
                if details.get('overview'):
                    st.markdown(f"**Overview:** {details.get('overview')}")
            else:
                st.markdown("Additional details not available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get and display recommendations when button is clicked
    if recommend_button:
        with st.spinner('Discovering perfect matches for you...'):
            names, posters, details = recommend(selected_movie_name)
        
        st.markdown("### 🎯 Your Personalized Recommendations")
        st.markdown("Based on your selection, we think you'll love these films:")
        
        # Display recommendations in a responsive grid
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" class="movie-poster" alt="{names[i]}">
                    <div class="movie-title">{names[i]}</div>
                    <div class="movie-meta">
                        {details[i]['release_date']} 
                        <span class="movie-rating">⭐ {details[i]['rating']}</span>
                    </div>
                    <div class="movie-overview scrollable-description">
                        {details[i]['overview'][:200] + '...' if len(details[i]['overview']) > 200 else details[i]['overview']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p>Created with 💙 by <a href="https://www.linkedin.com/in/ambadeaditya/" target="_blank">Tobi</a> | Powered by TMDB API</p>    
        <p>© 2025 Cinematic Compass</p>
    </div>
""", unsafe_allow_html=True)