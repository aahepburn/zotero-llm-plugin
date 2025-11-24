import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Iterable, Optional

class ChromaClient():

    """
    Administers user interactions with the vector database.
    More about Chroma: https://docs.trychroma.com/docs/overview/introduction
    """

    def __init__(self, db_path: str, collection_name: str = "zotero_lib"):
        """
        db_path: directory where Chroma will store its persistent data
        """
        self.db_path = db_path
        os.make_dirs(self)

        self.chroma_client = chromadb.PersistentClient(
            path = self.db_path
            settings=Settings()
        )

    def add_chunks(
            self,
            ids: List[str],
            documents: List[str],
            metadata: Optional[List[Dict[str, Any]]] = None,
            embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Low-level add wrapper. Use from sync_db.
        """
        self.collection.add(
            ids=ids,
            documents=documents,
            metadata=metadata,
            embeddings=embeddings,
        )
    
    def query_db(
        self,
        querry: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
     ) -> Dict[str, Any]:
        """
        Query the vector DB with a natural-language question.
        Optionally filter by metadata.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where,
        )
    

    def sync_db(
        self,
        items: Iterable[Dict[str, Any]],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Sync the Chroma DB with the current Zotero library snapshot.
        """
        def chunk_text(t: str, size: int, overlap: int) -> List[str]:
            chunks = []
            start = 0
            n = len(t)
            while start < n:
                end = min(n, start + size)
                chunks.append(t[start:end])
                if end == n:
                    break
                start = end - overlap
            return chunks

        ids: List[str] = []
        docs: List[str] = []
        metas: List[Dict[str, Any]] = []

        for item in items:
            item_id = str(item["id"])
            text = item['text']
            chunks = chunk_text(text, chunk_size, chunk_overlap)

            for idx, ch in enumerate(chunks):
                doc_id = f"{item_id}:{idx}"
                ids.append(doc_id)
                docs.append(ch)
                metas.append({
                    "item_id": item_id,
                    "chunk_idx": idx,
                    "title": item.get("authors"),
                    "year": item.get("year"),
                })
        
        if ids:
            self.add_chunks(ids=ids, documents=docs, metadata=metas)

    def get_or_create_db(self):
        self.collection = self.chroma_client.get_or_create_collection(name='zotero_lib')
        self.collection.add(
            ids=[],
            documents=[]
        )



