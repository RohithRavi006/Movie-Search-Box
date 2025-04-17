import streamlit as st
import requests
import webbrowser

API_URL = "http://localhost:8000"
st.set_page_config(page_title="Cinema Spotlight", layout="wide")

# ------------------ Enhanced Styling with New Background ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@600&display=swap');
    
    /* Modern Dark Theme */
    .stApp {
    background: 
        linear-gradient(rgba(15, 15, 35, 0.4), rgba(15, 15, 35, 0.5)),
        url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80') !important;
    background-size: cover !important;
    background-attachment: fixed !important;
    background-position: center !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    color: white !important;
}

    
    /* Film Strip Effect */
    .glass-box {
        background: rgba(15, 15, 35, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(245, 197, 24, 0.3) !important;
        border-radius: 8px !important;
        box-shadow: 
            0 0 15px rgba(245, 197, 24, 0.2),
            inset 0 0 20px rgba(255, 255, 255, 0.1) !important;
        position: relative;
        overflow: hidden;
    }
    
    .glass-box::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 20px;
        background: linear-gradient(
            to right,
            #000 0%, #000 10%,
            transparent 10%, transparent 20%,
            #000 20%, #000 30%,
            transparent 30%, transparent 40%,
            #000 40%, #000 50%,
            transparent 50%, transparent 60%,
            #000 60%, #000 70%,
            transparent 70%, transparent 80%,
            #000 80%, #000 90%,
            transparent 90%, transparent 100%
        );
        opacity: 0.3;
    }
    
    .glass-box::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 20px;
        background: linear-gradient(
            to right,
            #000 0%, #000 10%,
            transparent 10%, transparent 20%,
            #000 20%, #000 30%,
            transparent 30%, transparent 40%,
            #000 40%, #000 50%,
            transparent 50%, transparent 60%,
            #000 60%, #000 70%,
            transparent 70%, transparent 80%,
            #000 80%, #000 90%,
            transparent 90%, transparent 100%
        );
        opacity: 0.3;
    }
    
    /* Rest of your existing CSS styles... */
    /* [Keep all your other existing CSS styles exactly as they were] */
    </style>
""", unsafe_allow_html=True)

# ------------------ App Title ------------------
st.markdown("""
    <div style="text-align: center; margin: 1rem 0 2rem 0; position: relative;">
        <h1>🎬 CINEMA SPOTLIGHT</h1>
        <p style="font-size: 1.2rem; color: #aaa; letter-spacing: 2px; text-shadow: 0 0 5px rgba(0,0,0,0.5);">
            YOUR PERSONAL FILM ARCHIVE
        </p>
    </div>
""", unsafe_allow_html=True)

# [REST OF YOUR ORIGINAL CODE REMAINS EXACTLY THE SAME FROM THIS POINT ONWARD]
# [INCLUDE ALL YOUR EXISTING NAVIGATION, SESSION STATE, AND PAGE SECTIONS]

# ------------------ Navigation ------------------
nav = st.radio(
    "Navigate", 
    ["Search Movies", "Top Rated", "Movies by Actor", "Search History"],
    horizontal=True,
    label_visibility="hidden"
)

# ------------------ Session State ------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"

# ------------------ Reusable Card ------------------
def show_movie_card(movie):
    st.markdown(f"""
        <div class='card-text'>
            <div style="font-size: 1.4rem; color: #f5c518; margin-bottom: 0.5rem;">
                🎥 {movie['Name']}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                <div>📅 <strong>Year:</strong> {movie.get('Year', 'N/A')}</div>
                <div>🎬 <strong>Director:</strong> {movie.get('Director', 'N/A')}</div>
                <div>🎭 <strong>Genre:</strong> {movie.get('Genre', 'N/A')}</div>
                <div>⭐ <strong>IMDb:</strong> {movie.get('IMDb', 'N/A')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ------------------ Pages ------------------
if nav == "Search Movies":
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
    st.subheader("🍿 SEARCH MOVIES")
    search_input = st.text_input("Type movie name...", key="search_input")

    suggestions = []
    if search_input:
        try:
            response = requests.get(f"{API_URL}/search?prefix={search_input}&user_id={st.session_state.user_id}")
            suggestions = response.json().get("movies", [])
        except:
            st.error("Error fetching suggestions.")

    if suggestions:
        selected_movie = st.selectbox("Choose a Film", suggestions, key="movie_select")
        if selected_movie:
            try:
                movie_response = requests.get(f"{API_URL}/movie/{selected_movie}?user_id={st.session_state.user_id}")
                movie = movie_response.json()
                if "error" not in movie:
                    show_movie_card(movie)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("▶ WATCH TRAILER", key="trailer"):
                            webbrowser.open(movie.get("Trailer_URL", "#"))
                    with col2:
                        if st.button("🎵 PLAY SONG", key="song"):
                            webbrowser.open(movie.get("Famous_Song", "#"))
                else:
                    st.error("Movie not found.")
            except:
                st.error("Error fetching movie details.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Top Rated":
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
    st.subheader("🏆 TOP RATED MOVIES")
    n_movies = st.number_input("Number of Top Movies to Show:", 
                              min_value=1, max_value=20, 
                              value=10, step=1)
    
    if st.button("SHOW TOP FILMS"):
        try:
            response = requests.get(f"{API_URL}/top-rated?N={n_movies}")
            if response.status_code == 200:
                top_movies = response.json().get("top_movies", [])
                if not top_movies:
                    st.info("No rated movies found.")
                else:
                    cols = st.columns(2)
                    for idx, movie in enumerate(top_movies):
                        with cols[idx % 2]:
                            st.markdown(f"""
                                <div class="card-text">
                                    <div style="font-size: 1.3rem; color: #f5c518; margin-bottom: 0.5rem;">
                                        #{idx+1} {movie.get('Name', 'Unknown Movie')}
                                    </div>
                                    <div style="font-size: 1.1rem; display: flex; align-items: center;">
                                        <span style="font-size: 1.5rem; margin-right: 5px;">⭐</spana>
                                        <strong>{movie.get('IMDb', 'N/A')}</strong>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Failed to fetch top movies. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Movies by Actor":
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
    st.subheader("🎭 MOVIES BY ACTOR")
    actor_prefix = st.text_input("Enter Actor Name:", "", key="actor_input")
    matching_actors = []
    if actor_prefix:
        try:
            response = requests.get(f"{API_URL}/movies-by-actor?prefix={actor_prefix}&user_id={st.session_state.user_id}")
            data = response.json()
            matching_actors = data.get("actors", [])
        except Exception as e:
            st.error(f"Error fetching actor suggestions: {str(e)}")

    if matching_actors:
        selected_actor = st.selectbox("Pick an Actor", matching_actors, key="actor_select")
        try:
            response = requests.get(f"{API_URL}/movies-by-actor?prefix={selected_actor}&user_id={st.session_state.user_id}")
            data = response.json()
            movies = data.get("movies", [])
            
            cols = st.columns(2)
            for idx, movie in enumerate(movies):
                with cols[idx % 2]:
                    movie_name = movie.get("Name") if isinstance(movie, dict) else movie
                    st.markdown(f"""
                        <div class="card-text">
                            🎬 <strong>{movie_name}</strong>
                        </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading movies for actor: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Search History":
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
    st.subheader("🕘 SEARCH HISTORY")
    try:
        response = requests.get(f"{API_URL}/history?user_id={st.session_state.user_id}")
        history = response.json().get("history", [])
        if not history:
            st.info("Your search history is empty.")
        else:
            cols = st.columns(2)
            for idx, item in enumerate(history):
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="card-text">
                            🔍 {item}
                        </div>
                    """, unsafe_allow_html=True)
    except:
        st.error("Error fetching history.")
    st.markdown("</div>", unsafe_allow_html=True)

