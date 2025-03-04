from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

# **Connect to MongoDB**
client = MongoClient("mongodb://localhost:27017/")
db = client["Movie_Information"]
collection = db["movies"]

# **HashMap for Movie Lookup**
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

# **API Endpoints**
@app.get("/search")
def search_movies(prefix: str):
    return {"movies": trie.search(prefix)}

@app.get("/movie/{movie_name}")
def get_movie_details(movie_name: str):
    return movie_data.get(movie_name.lower(), {"error": "Movie not found"})
