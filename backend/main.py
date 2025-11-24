# uvicorn backend.main:app --reload

from fastapi import FastAPI, Query
from typing import Optional
from backend.zoteroitem import ZoteroItem
from backend.external_api_utils import fetch_google_book_reviews, fetch_semantic_scholar_data
from backend.pdf import PDF
from fastapi import FastAPI, Query
from typing import Optional
from backend.zotero_dbase import ZoteroLibrary
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Must match your browser's address bar exactly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    """
    Health check endpoint for Zotero LLM backend.
    """
    return {"msg": "Welcome to Zotero LLM Plugin backend"}


@app.get("/pdfsample")
def pdf_sample(
    filename: str = Query(..., description="Path to PDF file, e.g. backend/sample_pdfs/test_article.pdf"),
    max_chars: Optional[int] = Query(2000, description="Maximum number of characters to extract"),
):
    """
    Extracts sample text from a PDF for testing purposes.
    Returns a JSON object with extracted text or error message.
    """
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
    """
    Retrieves metadata from the ZoteroItem class.
    """
    try:
        item = ZoteroItem(filepath=filename)
        title = item.get_title()
        author = item.get_author()
        return {"title": title, 
                "author": author}
    except Exception as e:
        return {"error": str(e)}


# @app.get("/search")
# def search(query: str, top_k: int = 3):
#     """
#     Semantic search across embedded documents.
#     Returns top-k matches with their text and filenames.
#     """
#     try:
#         embedding = get_embedding(query)
#         results = collection.query(
#             query_embeddings=[embedding],
#             n_results=top_k
#         )
#         return {
#             "results": [
#                 {"text": doc, "filename": meta["filename"]}
#                 for doc, meta in zip(results["documents"][0], results["metadatas"][0])
#             ]
#         }
#     except Exception as e:
#         return {"error": str(e)}
    
@app.get("/search_items")
def search_items(
    authors: Optional[str] = Query("", description="Comma separated authors"),
    titles: Optional[str] = Query("", description="Comma separated titles"),
    dates: Optional[str] = Query("", description="Comma separated dates")
):
    """
    Query the Zotero library using authors, titles, and dates.
    Returns a list of parent items.
    """
    try:
        authors_list = [a.strip() for a in authors.split(",") if a.strip()]
        titles_list = [t.strip() for t in titles.split(",") if t.strip()]
        dates_list = [d.strip() for d in dates.split(",") if d.strip()]
        db_path = '/Users/aahepburn/Zotero/zotero.sqlite'
        zlib = ZoteroLibrary(db_path)
        results = zlib.search_parent_items(authors=authors_list, titles=titles_list, dates=dates_list)
        return {"results": set(results)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_gbook_reviews")
def get_reviews(query: str):
    """
    Makes a call to the Google Books API to retrieve reviews.
    """
    try:
        reviews = fetch_google_book_reviews()
        return
    
    except Exception as e:
        return {"error": str(e)}
        
