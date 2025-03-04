import streamlit as st
import requests
import webbrowser

# **FastAPI Backend URL**
API_URL = "http://localhost:8000"

# **Streamlit Page Config**
st.set_page_config(page_title="Movie Search System", layout="wide")

# **Title**
st.title("🎬 Movie Search System")
st.write("Search for your favorite movies and view their details!")

# **Search Box**
search_input = st.text_input("Enter Movie Name:", "")

# **Perform Auto-Complete Search**
if search_input:
    response = requests.get(f"{API_URL}/search?prefix={search_input}")
    if response.status_code == 200:
        movies = response.json().get("movies", [])
        if movies:
            selected_movie = st.selectbox("Select a Movie", movies)

            # **Fetch Movie Details**
            if selected_movie:
                movie_response = requests.get(f"{API_URL}/movie/{selected_movie}")
                if movie_response.status_code == 200:
                    movie = movie_response.json()
                    
                    if "error" not in movie:
                        # **Display Movie Details**
                        st.subheader(f"🎥 {movie['Name']}")
                        st.write(f"📅 Year: {movie.get('Year', 'N/A')}")
                        st.write(f"🎬 Director: {movie.get('Director', 'N/A')}")
                        st.write(f"🎭 Genre: {movie.get('Genre', 'N/A')}")
                        st.write(f"⭐ IMDb Rating: {movie.get('IMDb', 'N/A')}")

                        # **Watch Trailer Button**
                        if st.button("▶ Watch Trailer"):
                            webbrowser.open(movie.get("Trailer_URL", "#"))

                        # **Play Song Button**
                        if st.button("🎵 Play Song"):
                            webbrowser.open(movie.get("Famous_Song", "#"))
                    else:
                        st.error("Movie details not found.")
        else:
            st.warning("No matches found.")
    else:
        st.error("Error connecting to the backend.")
