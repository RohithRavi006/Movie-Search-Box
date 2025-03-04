# Group-15-AIE-D-OOPS-and-JAVA-
Project Name: Movie Search Box where we let the user an experience of searching the names of the movies and retrieve the information related to it.
# 🎬 Movie Search System (Streamlit + Trie + HashMap)

## **📌 Overview**
The **Movie Search System** is a **fast, intelligent search engine** for movies.  
It uses **Trie data structure** for **auto-complete search** and **HashMap (Python Dictionary)** for **instant movie details retrieval (`O(1)`)** instead of querying MongoDB every time.

## **🔥 Features**
✅ **Real-time Auto-Complete** (Using Trie)  
✅ **Instant Movie Lookup (`O(1)`)** (Using HashMap)  
✅ **Displays Movie Posters**  
✅ **YouTube Trailer & Song Links**  
✅ **Optimized for Large Datasets**  

---

## **📌 Technologies Used**
- **Frontend:** Streamlit (Python Web UI)  
- **Backend:** MongoDB (Database) + Trie & HashMap (Data Structures)  
- **Libraries:**  
  - `streamlit` → Web UI  
  - `pymongo` → MongoDB Connection  
  - `PIL` (Pillow) → Image Processing  
  - `webbrowser` → Open YouTube Trailer/Songs  

---

## **📌 Installation & Setup**
### **1️⃣ Install Dependencies**
Run the following command:
```sh
pip install streamlit pymongo pillow
