#vector_db.py
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Iterable, Optional

class ChromaClient:
    """
    Administers user interactions with the Chroma vector database for Zotero library items.
    Supports persistent per-library DB, bulk chunk addition, semantic querying, and sync with Zotero snapshot.
    """

    def __init__(self, db_path: str, collection_name: str = "zotero_lib"):
        self.db_path = db_path
        self.collection_name = collection_name
        os.makedirs(self.db_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.db_path, settings=Settings())
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def add_chunks(self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Bulk-adds document chunks and their vectors to the Chroma collection.
        """
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query_db(self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector DB with a natural-language question.
        Optionally filter by metadata keys (e.g. item_id).
        """
        results = self.collection.query(
            query_texts=[query], 
            n_results=k,
            where=where,
        )
        return results

    def sync_db(self,
        items: Iterable[Any],  
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embed_fn=None,
    ) -> None:
        """
        Syncs the Chroma DB with the current ZoteroItem snapshot.
        Indexes and chunks text, embeds with supplied function, and stores metadata.
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
        embeddings: List[List[float]] = []

        for item in items:
            text = getattr(item, "metadata", {}).get("text") or item.get("text") if isinstance(item, dict) else None
            item_id = getattr(item, "metadata", {}).get("item_id") or item.get("item_id") if isinstance(item, dict) else None
            if not text or not item_id:
                continue
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            meta_src = getattr(item, "metadata", {}) if hasattr(item, "metadata") else item
            ids_batch = []
            docs_batch = []
            metas_batch = []
            for idx, ch in enumerate(chunks):
                doc_id = f"{str(item_id)}:{str(idx)}"
                ids_batch.append(doc_id)
                docs_batch.append(ch)

                title = meta_src.get("title") or ""
                authors = meta_src.get("authors") or ""
                tags = meta_src.get("tags") or ""
                collections = meta_src.get("collections") or ""
                year = meta_src.get("date") or ""
                pdf_path = meta_src.get("pdf_path") or ""

                metas_batch.append({
                    "item_id": str(item_id),
                    "chunk_idx": int(idx),
                    "title": title,
                    "authors": authors,
                    "tags": tags,
                    "collections": collections,
                    "year": year,
                    "pdf_path": pdf_path,
                })
            ids += ids_batch
            docs += docs_batch
            metas += metas_batch
            # ----- Embed batch -----
            if embed_fn is not None and docs_batch:
                embeddings += self.embed_chunks(docs_batch, embed_fn)
        if ids:
            print("ID types:", set(type(i) for i in ids))
            self.add_chunks(
                ids=[str(i) for i in ids],
                documents=docs,
                metadatas=metas,
                embeddings=embeddings if embed_fn is not None else None
            )

    def get_or_create_db(self):
        """
        Ensures the collection exists and is initialized.
        """
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def embed_chunks(self, chunks: List[str], embed_fn) -> List[List[float]]:
        """
        Passes a list of text chunks through the embedding function and returns their vectors.
        """
        embeddings = [embed_fn(chunk) for chunk in chunks]
        return embeddings
