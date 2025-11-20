import requests
from semanticscholar import SemanticScholar
import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()

google_api_key = os.getenv("GOOGLE_API")

def fetch_google_book_reviews(isbn, google_api_key):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"
    resp = requests.get(url)
    data = resp.json()
    reviews = []
    for item in data.get('items', []):
        volume_info = item.get('volumeInfo', {})
        reviews.append({
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description', ''),
            'preview_link': volume_info.get('previewLink', ''),
            'info_link': volume_info.get('infoLink', '')
        })
    return reviews


def fetch_semantic_scholar_data(doi):
    sch = SemanticScholar()
    paper = sch.paper(doi)
    abstract = paper.get('abstract', '')
    citations = paper.get('citations', [])
    references = paper.get('references', [])
    return {
        'abstract': abstract,
        'citations': citations,
        'references': references,
    }

