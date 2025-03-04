

# 🎬 Movie Search System (Streamlit + Trie + HashMap + B-Trees + Graphs)

## **📌 Overview**
The **Movie Search System** is a **fast, intelligent search engine** for movies.  
It integrates **multiple Data Structures** to **enhance efficiency**:

✅ **Trie (`O(m)`)** → Auto-complete movie search  
✅ **HashMap (`O(1)`)** → Instant movie detail retrieval  
✅ **B-Trees (`O(log n)`)** → Optimized MongoDB queries  
✅ **Graphs (`O(V+E)`)** → Actor-Movie relationship mapping  

---

## **🔥 Features**
- ✅ **Real-time Auto-Complete Search** (Using Trie)  
- ✅ **Instant Movie Lookup (`O(1)`)** (Using HashMap)  
- ✅ **Optimized Movie Querying (`O(log n)`)** (Using B-Trees in MongoDB)  
- ✅ **Find Actor-Movie Connections (`O(V+E)`)** (Using Graphs)  
- ✅ **Displays Movie Posters**  
- ✅ **YouTube Trailer & Song Links**  
- ✅ **Optimized for Large Datasets**  

---

## **📌 Technologies Used**
- **Frontend:** Streamlit (Python Web UI)  
- **Backend:** MongoDB (Database) + Trie, HashMap, B-Trees, Graphs (Data Structures)  
- **Libraries:**  
  - `streamlit` → Web UI  
  - `pymongo` → MongoDB Connection  
  - `PIL (Pillow)` → Image Processing  
  - `networkx` → Graph Processing  
  - `webbrowser` → Open YouTube Trailer/Songs  

---

## **📌 Data Structure Concepts Used**
### **1️⃣ Trie (Auto-Complete)**
- **Used for:** Fast movie name search as the user types.
- **Time Complexity:** `O(m)`, where `m` is the prefix length.
- **Why?** Avoids slow MongoDB queries for real-time suggestions.

### **2️⃣ HashMap (Instant Lookup)**
- **Used for:** Fetching movie details instantly.
- **Time Complexity:** `O(1)`.
- **Why?** Prevents repeated MongoDB queries.

### **3️⃣ B-Trees (MongoDB Indexing)**
- **Used for:** Optimized movie search in MongoDB.
- **Time Complexity:** `O(log n)`, since MongoDB uses **B-Trees for indexing**.
- **Why?** Fast searches without scanning the entire database.

### **4️⃣ Graphs (Actor-Movie Relationships)**
- **Used for:** Finding **connections between actors & movies**.
- **Time Complexity:** `O(V + E)`, where `V` = number of actors, `E` = number of movies.
- **Why?** Helps in recommending movies based on actors.

---

## **📌 MongoDB Database Setup**
### **1️⃣ Connect to MongoDB**
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Movie_Information"]
collection = db["movies"]


movies = [
    {"Name": "Inception", "Year": 2010, "Director": "Christopher Nolan", "Genre": "Sci-Fi", "IMDb": 8.8, "Trailer_URL": "https://youtu.be/YoHD9XEInc0", "Famous_Song": "https://youtu.be/8hP9D6kZseM"},
    {"Name": "Interstellar", "Year": 2014, "Director": "Christopher Nolan", "Genre": "Sci-Fi", "IMDb": 8.6, "Trailer_URL": "https://youtu.be/zSWdZVtXT7E", "Famous_Song": "https://youtu.be/Lm8p5rlrSkY"}
]

collection.insert_many(movies)
print("✅ Movies inserted successfully!")


---

## **📌 Installation & Setup**
### **1️⃣ Install Dependencies**
Run the following command:
```sh
pip install streamlit pymongo pillow
