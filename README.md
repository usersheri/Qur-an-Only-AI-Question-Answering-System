<img width="2402" height="1642" alt="Screenshot 2026-01-03 220358" src="https://github.com/user-attachments/assets/f859a393-0523-4e0f-9c5e-2d14ef7a470a" />

# Quran AI Backend

A Quran-only GenAI backend built with Python and FastAPI that performs:
- **Quran-based Q&A** using semantic search
- **Surah and Ayah summaries** based solely on Quran text
- **Favorites storage** for bookmarking ayahs

## ⚠️ Critical Religious Constraints

1. **Uses ONLY the provided Quran text** - No Hadith, Tafsir, scholarly opinion, or external knowledge
2. **Strict responses** - If something is not explicitly in the Quran, responds: "The Qur'an does not explicitly mention this."
3. **Language**: English
4. **Always shows**: Arabic text, English translation, Surah number and Ayah number

## 📋 Prerequisites

- Python 3.8 or higher
- Existing Quran data files in `/data` directory:
  - `quran-uthmani.txt` (Arabic text, format: `surah|ayah|arabic_text`)
  - `en.sahih.txt` (English translation, format: `surah|ayah|english_text`)

## 🚀 Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Note: The first run will download the SentenceTransformer model (~90MB) for embeddings.

## 📁 Project Structure

```
quran_ai/
│
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── qa.py            # Q&A endpoint
│   │   ├── summary.py       # Summary endpoints
│   │   ├── favorites.py     # Favorites endpoints
│   ├── core/
│   │   ├── quran_loader.py  # Loads existing data files
│   │   ├── normalizer.py    # Normalizes to internal structure
│   │   ├── embeddings.py    # SentenceTransformers integration
│   │   ├── vector_store.py  # FAISS vector store
│   │   ├── prompt.py        # Quran-only prompts
│   │   ├── llm.py           # LLM integration (simple fallback)
│   ├── models/
│   │   ├── schemas.py       # Pydantic schemas
│
├── data/                    # Your existing Quran data files
│   ├── quran-uthmani.txt
│   └── en.sahih.txt
│
├── requirements.txt
└── README.md
```

## 🏃 Running the Application

Start the FastAPI server:

```bash
python -m quran_ai.app.main
```

Or using uvicorn directly:

```bash
uvicorn quran_ai.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Note**: The first startup will:
1. Load and normalize all Quran data
2. Generate embeddings for all 6236 ayahs (takes ~2-5 minutes)
3. Build and cache the FAISS vector store

Subsequent startups will load the cached vector store (much faster).

## 📚 API Endpoints

### 1. Q&A Endpoint

**POST** `/qa`

Ask a question and get an answer based on Quran text only.

**Request**:
```json
{
  "question": "What does the Quran say about patience?"
}
```

**Response**:
```json
{
  "question": "What does the Quran say about patience?",
  "answer": "Based on the Qur'an:\n\n**Surah Al-Baqarah (2:153):**\nArabic: ...\nEnglish: O you who have believed, seek help through patience and prayer...\n\n...",
  "relevant_ayahs": [
    {
      "id": "2:153",
      "surah": 2,
      "surah_name": "Al-Baqarah",
      "ayah": 153,
      "arabic": "...",
      "english": "..."
    }
  ]
}
```

### 2. Summary Endpoints

**GET** `/summary/surah/{surah_number}`

Summarize a surah (1-114).

**Example**: `GET /summary/surah/1`

**Response**:
```json
{
  "summary": "Summary based on Quran text only...",
  "ayahs": [...]
}
```

**GET** `/summary/ayah/{surah}/{ayah}`

Summarize a specific ayah.

**Example**: `GET /summary/ayah/2/255`

**Response**:
```json
{
  "summary": "Summary based on Quran text only...",
  "ayahs": [...]
}
```

### 3. Favorites Endpoints

**POST** `/favorites`

Add an ayah to favorites.

**Request**:
```json
{
  "ayah_id": "2:255"
}
```

**GET** `/favorites`

Get all favorite ayahs.

**Response**:
```json
{
  "favorites": [
    {
      "ayah_id": "2:255",
      "ayah": {
        "id": "2:255",
        "surah": 2,
        "surah_name": "Al-Baqarah",
        "ayah": 255,
        "arabic": "...",
        "english": "..."
      }
    }
  ]
}
```

**DELETE** `/favorites/{ayah_id}`

Remove an ayah from favorites.

### 4. Health Check

**GET** `/health`

Check if the backend is initialized and ready.

**GET** `/`

Root endpoint with API information.

## 🔧 Example API Requests

### Using curl

**Q&A**:
```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the Quran say about mercy?"}'
```

**Surah Summary**:
```bash
curl "http://localhost:8000/summary/surah/1"
```

**Ayah Summary**:
```bash
curl "http://localhost:8000/summary/ayah/2/255"
```

**Add Favorite**:
```bash
curl -X POST "http://localhost:8000/favorites" \
  -H "Content-Type: application/json" \
  -d '{"ayah_id": "2:255"}'
```

**Get Favorites**:
```bash
curl "http://localhost:8000/favorites"
```

### Using Python requests

```python
import requests

# Q&A
response = requests.post("http://localhost:8000/qa", json={
    "question": "What does the Quran say about patience?"
})
print(response.json())

# Summary
response = requests.get("http://localhost:8000/summary/surah/1")
print(response.json())

# Add favorite
response = requests.post("http://localhost:8000/favorites", json={
    "ayah_id": "2:255"
})
print(response.json())
```

## 🛠️ Technical Details

### Data Loading
- Reads existing pipe-separated text files (`surah|ayah|text`)
- Normalizes into internal `AyahModel` structure
- Preserves original files (no modifications)

### Embeddings
- Uses **SentenceTransformers** (`all-MiniLM-L6-v2` model)
- Generates embeddings for English translations (for semantic search)
- Caches embeddings in FAISS vector store

### Vector Search
- Uses **FAISS** (Facebook AI Similarity Search) for fast similarity search
- L2 distance metric
- Cached to disk for faster startup

### LLM Integration
- Currently uses a simple formatter (no heavy LLM model required)
- Can be extended to use `mistral-7b-instruct`, `llama.cpp`, or HuggingFace models
- All responses strictly based on retrieved Quran text only

### Storage
- **Favorites**: SQLite database (`favorites.db`)
- **Vector Store**: FAISS index (`vector_store.faiss`)

## 📝 Notes

- **First startup**: Takes 2-5 minutes to generate embeddings for all ayahs
- **Subsequent startups**: Much faster (loads cached vector store)
- **Memory usage**: ~500MB-1GB (depending on models)
- **No paid APIs**: All tools are free/open-source

## 🔒 Religious Compliance

This backend strictly adheres to:
- ✅ Uses ONLY Quran text
- ✅ No external knowledge or interpretation
- ✅ Explicit "not mentioned" responses when appropriate
- ✅ Always shows Arabic + English + Surah/Ayah numbers

## 🐛 Troubleshooting

**Issue**: "Data files not found"
- Ensure `data/quran-uthmani.txt` and `data/en.sahih.txt` exist
- Check file paths are correct

**Issue**: "Vector store not loading"
- Delete `vector_store.faiss` and `vector_store.faiss.ids.pkl` to rebuild
- Ensure sufficient disk space

**Issue**: "Embedding generation slow"
- This is normal on first run (6236 ayahs)
- Subsequent runs use cached embeddings

## 📄 License

This project is for educational and personal use.

---

**Built with**: FastAPI, SentenceTransformers, FAISS, Python

<img width="2665" height="1694" alt="Screenshot 2026-01-03 220550" src="https://github.com/user-attachments/assets/2d52319f-4115-438e-b7b4-1ef593548fae" />




