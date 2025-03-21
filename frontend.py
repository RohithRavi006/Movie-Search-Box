import streamlit as st
import requests
import webbrowser

# *Backend API URL*
API_URL = "http://localhost:8000"

# *Streamlit Page Configuration*
st.set_page_config(page_title="Movie Search System", layout="wide")

# *Title*
st.title("🎬 Movie Search System")
st.write("Search for your favorite movies and view their details!")

# *Search Box for Movies*
search_input = st.text_input("Enter Movie Name:", "")

# *Perform Auto-Complete Search*
if search_input:
    try:
        response = requests.get(f"{API_URL}/search?prefix={search_input}", timeout=5)
        response.raise_for_status()
        movies = response.json().get("movies", [])

        if movies:
            selected_movie = st.selectbox("Select a Movie", movies)

            # *Fetch Movie Details*
            if selected_movie:
                movie_response = requests.get(f"{API_URL}/movie/{selected_movie}", timeout=5)
                movie_response.raise_for_status()
                movie = movie_response.json()

                if "error" not in movie:
                    # *Display Movie Details*
                    st.subheader(f"🎥 {movie['Name']}")
                    st.write(f"📅 Year: {movie.get('Year', 'N/A')}")
                    st.write(f"🎬 Director: {movie.get('Director', 'N/A')}")
                    st.write(f"🎭 Genre: {movie.get('Genre', 'N/A')}")
                    st.write(f"⭐ IMDb Rating: {movie.get('IMDb', 'N/A')}")

                    # *Watch Trailer Button*
                    if st.button("▶ Watch Trailer"):
                        webbrowser.open(movie.get("Trailer_URL", "#"))

                    # *Play Song Button*
                    if st.button("🎵 Play Song"):
                        webbrowser.open(movie.get("Famous_Song", "#"))
                else:
                    st.error("Movie details not found.")
        else:
            st.warning("No matches found.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")

# *Sidebar - Top Rated Movies*
if st.sidebar.button("🔥 Show Top-Rated Movies"):
    try:
        top_response = requests.get(f"{API_URL}/top-rated", timeout=5)
        top_response.raise_for_status()
        top_movies = top_response.json().get("top_movies", [])

        if top_movies:
            st.sidebar.subheader("📌 Top Movies")
            for movie in top_movies:
                st.sidebar.write(f"🎬 {movie['Name']} - ⭐ {movie['IMDb']}")
        else:
            st.sidebar.warning("No top-rated movies found.")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Error fetching top-rated movies: {e}")

# *Movies by Actor*
actor_name = st.text_input("🔍 Search Movies by Actor", "")

if actor_name:
    try:
        actor_response = requests.get(f"{API_URL}/movies-by-actor?name={actor_name}", timeout=5)
        actor_response.raise_for_status()
        actor_movies = actor_response.json().get("movies", [])

        if actor_movies:
            st.subheader(f"🎭 Movies featuring {actor_name}")
            for movie in actor_movies:
                st.write(f"🎬 {movie}")
        else:
            st.warning("No movies found for this actor.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movies for actor: {e}")

# *Recommended Movies Based on Co-Actors*
recommend_actor = st.text_input("🤝 Recommend Movies Based on Actor", "")

if recommend_actor:
    try:
        recommend_response = requests.get(f"{API_URL}/recommend-movies?name={recommend_actor}", timeout=5)
        recommend_response.raise_for_status()
        recommended_movies = recommend_response.json().get("recommended_movies", [])

        if recommended_movies:
            st.subheader(f"📌 Recommended Movies for {recommend_actor}")
            for movie in recommended_movies:
                st.write(f"🎬 {movie}")
        else:
            st.warning("No recommendations available.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recommendations: {e}")
