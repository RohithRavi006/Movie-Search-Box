from flask import Flask, jsonify, request, send_from_directory
from pymongo import MongoClient
import networkx as nx
from flask_cors import CORS
import logging
import os
from heapq import heappush, heappop

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ------------------ MongoDB Connection Class ------------------

class MovieDataManager:
    def __init__(self, db_url="mongodb://localhost:27017/", db_name="Movie_Information", collection_name="movies"):
        self.db_url = db_url
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.movie_data = {}
        
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.client = MongoClient(self.db_url, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Will throw an exception if connection is failed
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Connected to MongoDB successfully")
            self.load_movie_data()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.collection = None

    def load_movie_data(self):
        if self.collection is not None:
            try:
                self.movie_data = {movie["Name"].lower(): movie for movie in self.collection.find({}, {"_id": 0})}
                logger.info(f"Loaded {len(self.movie_data)} movies into memory")
            except Exception as e:
                logger.error(f"Failed to load movie data: {e}")
    
    def get_movie_data(self):
        return self.movie_data

# ------------------ Trie Structure Encapsulation ------------------

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.movie_names = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, name):
        node = self.root
        for char in name.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.movie_names.append(name)

    def search(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_names(node)

    def _collect_names(self, node):
        results = []
        if node.is_end:
            results.extend(node.movie_names)
        for child in node.children.values():
            results.extend(self._collect_names(child))
        return results

class MovieTrieManager:
    def __init__(self):
        self.movie_trie = Trie()
        self.actor_trie = Trie()

    def insert_movie(self, movie_name):
        self.movie_trie.insert(movie_name)

    def search_movies(self, prefix):
        return self.movie_trie.search(prefix)

    def insert_actor(self, actor_name):
        self.actor_trie.insert(actor_name)

    def search_actors(self, prefix):
        return self.actor_trie.search(prefix)

# ------------------ Graph Encapsulation ------------------

class MovieGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.all_actors = set()

    def add_movie(self, movie_name):
        self.graph.add_node(movie_name, type="movie")

    def add_actor(self, actor_name):
        self.graph.add_node(actor_name, type="actor")

    def add_edge(self, actor_name, movie_name):
        self.graph.add_edge(actor_name, movie_name)

    def get_movies_by_actor(self, actor_name):
        if actor_name in self.graph and self.graph.nodes[actor_name].get("type") == "actor":
            return [node for node in self.graph.neighbors(actor_name) if self.graph.nodes[node]["type"] == "movie"]
        return []

    def get_graph(self):
        return self.graph

# ------------------ Priority Queue Implementation ------------------

class PriorityQueueItem:
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data
    
    def __lt__(self, other):
        # This makes the heap a min-heap (lower priority numbers come first)
        return self.priority < other.priority

class MoviePriorityQueue:
    def __init__(self):
        self._heap = []  # Private attribute (internal use only)
        self._size = 0   # Private attribute (internal use only)
    
    def enqueue(self, priority, data):
        """Add an item to the priority queue with the given priority."""
        item = PriorityQueueItem(priority, data)
        heappush(self._heap, item)
        self._size += 1 
    
    def dequeue(self):
        """Remove and return the item with the highest priority (lowest number)."""
        if self._size == 0:
            raise IndexError("Priority queue is empty")
        item = heappop(self._heap)  
        self._size -= 1
        return item.data
    
    def peek(self):
        """Return the item with the highest priority without removing it."""
        if self._size == 0:
            raise IndexError("Priority queue is empty")
        return self._heap[0].data
    
    def is_empty(self):
        """Check if the priority queue is empty."""
        return self._size == 0
    
    def __len__(self):
        """Return the number of items in the priority queue."""
        return self._size
    
    def clear(self):
        """Remove all items from the priority queue."""
        self._heap = []
        self._size = 0

# ------------------ Search History Encapsulation ------------------

class SearchHistoryManager:
    def __init__(self):
        self._search_history = {}  

    def save_search(self, user_id, movie_name):
        if not movie_name or not isinstance(movie_name, str):
            return False
        try:
            if user_id not in self._search_history:
                self._search_history[user_id] = []
            if movie_name.lower() not in [m.lower() for m in self._search_history[user_id]]:
                self._search_history[user_id].append(movie_name)
            return True
        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            return False

    def get_search_history(self, user_id):
        try:
            return self._search_history.get(user_id, [])
        except Exception as e:
            logger.error(f"Failed to get search history: {e}")
            return []



# ------------------ Initialize Managers ------------------
movie_data_manager = MovieDataManager()
movie_trie_manager = MovieTrieManager()
movie_graph = MovieGraph()
search_history_manager = SearchHistoryManager()
movie_priority_queue = MoviePriorityQueue()

# Initialize data
def build_graph_and_tries():
    if not movie_data_manager.get_movie_data():
        logger.warning("No movie data to build graph and tries")
        return
    
    for movie in movie_data_manager.get_movie_data().values():
        movie_name = movie["Name"].lower()
        movie_trie_manager.insert_movie(movie_name)
        movie_graph.add_movie(movie_name)
        actors = movie.get("Actors", [])
        if isinstance(actors, str):
            actors = [actor.strip().lower() for actor in actors.split(",")]
        elif isinstance(actors, list):
            actors = [actor.strip().lower() for actor in actors]
        for actor in actors:
            if actor:
                movie_graph.add_actor(actor)
                movie_graph.add_edge(actor, movie_name)
                movie_trie_manager.insert_actor(actor)
                movie_graph.all_actors.add(actor)

    logger.info(f"Graph built with {movie_graph.get_graph().number_of_nodes()} nodes and {movie_graph.get_graph().number_of_edges()} edges")

build_graph_and_tries()

# ------------------ API Endpoints ------------------
@app.route("/top-rated", methods=["GET"])
def get_top_rated_movies():
    try:
        n = int(request.args.get("N", 10))
        all_movies = list(movie_data_manager.get_movie_data().values())
        
        # Use the priority queue
        temp_queue = MoviePriorityQueue()
        
        for movie in all_movies:
            try:
                if 'IMDb' in movie and movie['IMDb']:
                    imdb_score = float(movie['IMDb'])
                    name = movie.get('Name', 'Unknown Movie')
                    # Use -imdb_score to make high scores come out first
                    temp_queue.enqueue(-imdb_score, {
                        'Name': name,
                        'IMDb': imdb_score
                    })
            except (ValueError, TypeError):
                continue

        # Get top N by dequeuing
        top_movies = []
        for _ in range(min(n, len(temp_queue))):
            top_movies.append(temp_queue.dequeue())

        return jsonify({"top_movies": top_movies})
    
    except Exception as e:
        logger.error(f"Top-rated endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/search", methods=["GET"])
def search_movies():
    try:
        prefix = request.args.get("prefix", "").lower()
        user_id = request.args.get("user_id", "default_user")
        movies = movie_trie_manager.search_movies(prefix)
        if movies and len(prefix) > 2:
            search_history_manager.save_search(user_id, movies[0])
        return jsonify({"movies": movies})
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/movie/<string:movie_name>", methods=["GET"])
def get_movie_details(movie_name):
    try:
        user_id = request.args.get("user_id", "default_user")
        search_history_manager.save_search(user_id, movie_name)
        movie = movie_data_manager.get_movie_data().get(movie_name.lower(), {"error": "Movie not found"})
        return jsonify(movie)
    except Exception as e:
        logger.error(f"Movie details endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/movies-by-actor", methods=["GET"])
def movies_by_actor():
    try:
        prefix = request.args.get("prefix", "").strip().lower()
        user_id = request.args.get("user_id", "default_user")
        if not prefix:
            return jsonify({"actors": [], "movies": [], "message": "Please provide an actor prefix"})
        
        matching_actors = movie_trie_manager.search_actors(prefix)
        if not matching_actors:
            return jsonify({"actors": [], "movies": [], "message": "No actors found"})

        selected_actor = prefix if prefix in movie_graph.all_actors else matching_actors[0]
        movies = movie_graph.get_movies_by_actor(selected_actor)
        
        # Convert movie names to original case from the database
        original_case_movies = []
        for movie_lower in movies:
            for movie_name in movie_data_manager.get_movie_data().keys():
                if movie_name.lower() == movie_lower:
                    original_case_movies.append(movie_name)
                    break

        return jsonify({
            "actors": matching_actors,
            "movies": original_case_movies
        })
    except Exception as e:
        logger.error(f"Movies-by-actor endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/history", methods=["GET"])
def search_history_endpoint():
    try:
        user_id = request.args.get("user_id", "default_user")
        history = search_history_manager.get_search_history(user_id)
        return jsonify({"history": history})
    except Exception as e:
        logger.error(f"Search-history endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500



# ------------------ Run App ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
