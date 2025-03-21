
from flask import Flask, jsonify, request
from pymongo import MongoClient
import heapq
import networkx as nx
from flask_cors import CORS  # To allow requests from frontend

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# **Connect to MongoDB**
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Movie_Information"]
    collection = db["movies"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    collection = None

# **HashMap for Movie Lookup**
movie_data = {}
if collection is not None:
    movie_data = {movie["Name"].lower(): movie for movie in collection.find({}, {"_id": 0})}

# **Trie for Auto-Complete**
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.movie_names = []

class MovieTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, movie_name):
        node = self.root
        for char in movie_name.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.movie_names.append(movie_name)

    def search(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return self.collect_movie_names(node)

    def collect_movie_names(self, node):
        results = []
        if node.is_end:
            results.extend(node.movie_names)
        for child in node.children.values():
            results.extend(self.collect_movie_names(child))
        return results

# **Initialize Trie**
trie = MovieTrie()
for movie_name in movie_data.keys():
    trie.insert(movie_name)

# **Priority Queue for Top Rated Movies**
def get_top_rated_movies(N=10):
    """Fetch the top N highest-rated movies based on IMDb score."""
    movie_list = list(movie_data.values())  # Convert HashMap to list
    top_movies = heapq.nlargest(N, movie_list, key=lambda x: x.get("IMDb", 0))
    return [{"Name": movie["Name"], "IMDb": movie.get("IMDb", "N/A")} for movie in top_movies]

# **Graph (Movie-Actor Connections)**
G = nx.Graph()

# **Build Graph: Add Nodes & Edges**
for movie in movie_data.values():
    movie_name = movie["Name"]
    G.add_node(movie_name, type="movie")
    
    for actor in movie.get("Actors", []):
        G.add_node(actor, type="actor")
        G.add_edge(actor, movie_name)  # Connect actor to movie

# **Find Movies by Actor**
def get_movies_by_actor(actor_name):
    """Find all movies in which the given actor has acted."""
    if actor_name in G:
        return [node for node in G.neighbors(actor_name) if G.nodes[node]['type'] == 'movie']
    return []

# **Recommend Movies Based on Co-Actors**
def recommend_movies(actor_name):
    """Find movies featuring actors who worked with the given actor."""
    recommended_movies = set()
    
    if actor_name in G:
        for movie in get_movies_by_actor(actor_name):
            for co_actor in G.neighbors(movie):
                if co_actor != actor_name and G.nodes[co_actor]["type"] == "actor":
                    recommended_movies.update(get_movies_by_actor(co_actor))
    
    return list(recommended_movies - set(get_movies_by_actor(actor_name)))  # Exclude already watched movies

# **API Endpoints**
@app.route("/search", methods=["GET"])
def search_movies():
    prefix = request.args.get("prefix", "")
    return jsonify({"movies": trie.search(prefix)})

@app.route("/movie/<string:movie_name>", methods=["GET"])
def get_movie_details(movie_name):
    return jsonify(movie_data.get(movie_name.lower(), {"error": "Movie not found"}))

@app.route("/top-rated", methods=["GET"])
def top_rated_movies():
    N = int(request.args.get("N", 10))
    return jsonify({"top_movies": get_top_rated_movies(N)})

@app.route("/movies-by-actor", methods=["GET"])
def movies_by_actor():
    name = request.args.get("name", "")
    return jsonify({"movies": get_movies_by_actor(name)})

@app.route("/recommend-movies", methods=["GET"])
def recommend_movies_by_actor():
    name = request.args.get("name", "")
    return jsonify({"recommended_movies": recommend_movies(name)})

# **Run the Flask App**
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
