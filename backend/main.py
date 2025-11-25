# backend/main.py
# uvicorn backend.main:app --reload
from fastapi import FastAPI, Query
from typing import Optional
from backend.zoteroitem import ZoteroItem
from backend.external_api_utils import fetch_google_book_reviews, fetch_semantic_scholar_data
from backend.pdf import PDF
from backend.zotero_dbase import ZoteroLibrary
from fastapi.middleware.cors import CORSMiddleware
from backend.interface import ZoteroChatbot
from backend.embed_utils import get_embedding

app = FastAPI() 

# CORS setup: matches your frontend HTML server (e.g., http://localhost:8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/Users/aahepburn/Zotero/zotero.sqlite"
CHROMA_PATH = "/Users/aahepburn/.zotero-llm/chroma/user-1"

# Instantiate the main chatbot object
chatbot = ZoteroChatbot(DB_PATH, CHROMA_PATH)

@app.get("/")
def read_root():
    """Health check endpoint for Zotero LLM backend."""
    return {"msg": "Welcome to Zotero LLM Plugin backend"}

@app.get("/pdfsample")
def pdf_sample(
    filename: str = Query(..., description="Path to PDF file, e.g. backend/sample_pdfs/test_article.pdf"),
    max_chars: Optional[int] = Query(2000, description="Maximum number of characters to extract"),
):
    """Extracts sample text from a PDF for testing purposes."""
    try:
        pdf = PDF(filepath=filename)
        text = pdf.extract_text(max_chars=max_chars)
        return {"sample": text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/item_metadata")
def get_item_metadata(
    filename: str = Query(..., description="Path to PDF or metadata file"),
):
    """Retrieves metadata from the ZoteroItem class."""
    try:
        item = ZoteroItem(filepath=filename)
        title = item.get_title()
        author = item.get_author()
        return {"title": title, 
                "author": author}
    except Exception as e:
        return {"error": str(e)}

@app.get("/search_items")
def search_items(
    authors: Optional[str] = Query("", description="Comma separated authors"),
    titles: Optional[str] = Query("", description="Comma separated titles"),
    dates: Optional[str] = Query("", description="Comma separated dates")
):
    """Query the Zotero library using authors, titles, and dates."""
    try:
        authors_list = [a.strip() for a in authors.split(",") if a.strip()]
        titles_list = [t.strip() for t in titles.split(",") if t.strip()]
        dates_list = [d.strip() for d in dates.split(",") if d.strip()]
        # Fix SQLite threading issue: check_same_thread=False inside ZoteroLibrary class!
        zlib = ZoteroLibrary(DB_PATH)
        results = zlib.search_parent_items(authors=authors_list, titles=titles_list, dates=dates_list)
        return {"results": list(results)}  # Convert set to list for JSON serialization
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_gbook_reviews")
def get_reviews(query: str):
    """Makes a call to the Google Books API to retrieve reviews."""
    try:
        reviews = fetch_google_book_reviews(query)
        return {"reviews": reviews}
    except Exception as e:
        return {"error": str(e)}

@app.post("/index_library")
def index_library():
    """Index all Zotero parent items and PDFs in the vector database."""
    try:
        chatbot.index_library()  # Make sure this is thread-safe if you use concurrency!
        return {"msg": "Indexing complete."}
    except Exception as e:
        return {"error": str(e)}

import traceback

@app.get("/chat")
def chat(query: str, item_ids: Optional[str] = Query("", description="Comma separated Zotero item IDs to scope search")):
    try:
        filter_ids = [id_.strip() for id_ in item_ids.split(",") if id_.strip()]
        payload = chatbot.chat(query, filter_item_ids=filter_ids if filter_ids else None)
        return payload
    except Exception as e:
        tb = traceback.format_exc()
        return {"error": str(e), "traceback": tb}


