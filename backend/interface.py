# interface.py

from backend.zotero_dbase import ZoteroLibrary
from backend.zoteroitem import ZoteroItem
from backend.pdf import PDF
from backend.vector_db import ChromaClient
from backend.embed_utils import get_embedding
from backend.local_llm import generate_answer
import os
from collections import OrderedDict
import threading
import time

class ZoteroChatbot:
    def __init__(self, db_path, chroma_path):
        self.zlib = ZoteroLibrary(db_path)
        self.chroma = ChromaClient(chroma_path)
        # Indexing state for reporting progress via /index_status
        self.is_indexing = False
        # Cancellation flag for background indexing
        self._cancel_indexing = False
        # Optional: simple progress counter (chunks processed)
        self.index_progress = {
            "processed_items": 0,
            "total_items": 0,
        }
        self._index_thread = None
    
    def _index_library_worker(self):
        try:
            raw_items = self.zlib.search_parent_items_with_pdfs()
            self.index_progress["total_items"] = len(raw_items)
            self.index_progress["processed_items"] = 0
            items = [ZoteroItem(filepath=it['pdf_path'], metadata=it) for it in raw_items]

            # Extract text for each item using PDF logic
            for item in items:
                if self._cancel_indexing:
                    break
                if not (item.filepath and os.path.exists(item.filepath)):
                    self.index_progress["processed_items"] += 1
                    continue  # Skip missing or inaccessible PDFs
                pdf = PDF(item.filepath)
                text = pdf.extract_text()
                item.metadata['text'] = text if text else ""

            # Vectorize each item's text (chunk/embedding logic)
            for item in items:
                if self._cancel_indexing:
                    break
                text = item.metadata.get('text') or ""
                if not text:
                    self.index_progress["processed_items"] += 1
                    continue
                chunks = self.chunk_text(text)
                if not chunks:
                    self.index_progress["processed_items"] += 1
                    continue
                vectors = [get_embedding(chunk) for chunk in chunks]

                # Generate unique chunk IDs
                item_id = str(item.metadata.get('item_id'))
                chunk_ids = [f"{item_id}:{i}" for i in range(len(chunks))]

                # Sanitize metadata per chunk to primitives, no None
                meta_src = item.metadata
                title = meta_src.get("title") or ""
                authors = meta_src.get("authors") or ""
                tags = meta_src.get("tags") or ""
                collections = meta_src.get("collections") or ""
                year = meta_src.get("date") or ""
                pdf_path = meta_src.get("pdf_path") or ""

                metas = []
                for i in range(len(chunks)):
                    metas.append({
                        "item_id": item_id,
                        "chunk_idx": int(i),
                        "title": title,
                        "authors": authors,
                        "tags": tags,
                        "collections": collections,
                        "year": year,
                        "pdf_path": pdf_path,
                    })

                self.chroma.add_chunks(
                    ids=chunk_ids,
                    documents=chunks,
                    metadatas=metas,
                    embeddings=vectors
                )
                # Update progress after processing this item
                self.index_progress["processed_items"] += 1
                # small sleep to allow cancellation to be checked promptly in CPU-bound loops
                time.sleep(0)
        finally:
            self.is_indexing = False
            self._cancel_indexing = False

    def start_indexing(self):
        """Start indexing in a background thread. No-op if already indexing."""
        if self.is_indexing:
            return
        self.is_indexing = True
        self._cancel_indexing = False
        # Reset progress
        self.index_progress = {"processed_items": 0, "total_items": 0}
        t = threading.Thread(target=self._index_library_worker, daemon=True)
        self._index_thread = t
        t.start()

    def cancel_indexing(self):
        """Signal cancellation for the running indexing job."""
        if not self.is_indexing:
            return
        self._cancel_indexing = True

    def chunk_text(self, text, chunk_size=512, overlap=64):
        # Naive chunking function
        chunks = []
        if not text:
            return chunks
        step = max(1, chunk_size - overlap)
        for i in range(0, len(text), step):
            chunks.append(text[i:i+chunk_size])
        return chunks

    def build_search_prompt(self, user_query: str) -> str:
        base = user_query.strip()
        if not base.endswith("?"):
            base += "?"
        return (
            "You are a professional research assistant. Answer this question using my Zotero papers as sources. "
            "Focus on concise, factual explanation suitable for an academic summary. "
            f"Question: {base}"
        )

    def build_answer_prompt(self, question: str, snippets: list[dict]) -> str:
        # Prompt that will be sent to Ollama
        if not snippets:
            return (
                "You are an academic assistant. The user asked a question, "
                "but there is no relevant context from their Zotero library. "
                "Explain that you cannot answer from their papers and suggest they add relevant articles.\n\n"
                f"Question: {question}"
            )

        context_blocks = []
        for s in snippets:
            cid = s["citation_id"]
            title = s.get("title", "Untitled")
            year = s.get("year", "")
            txt = s.get("snippet", "")
            context_blocks.append(f"[{cid}] {title} ({year}): {txt}")

        context = "\n\n".join(context_blocks)
        return (
            "You are a professional research assistant answering questions using ONLY the context below, "
            "taken from the user's Zotero library.\n"
            "Write a clear, readable answer with:\n"
            "- 1–2 sentences that directly answer the question.\n"
            "- Then 2–4 short bullet points highlighting key details.\n"
            "When you state a fact, cite the supporting sources using their IDs in brackets, e.g., [1]. "
            "If the answer is not in the context, explicitly say you cannot answer from these papers.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}\n\n"
            "Answer:"
        )




    def chat(self, query, filter_item_ids=None):
        # 1) Retrieve relevant chunks from Chroma
        db_filter = {"item_id": {"$in": filter_item_ids}} if filter_item_ids else None
        search_prompt = self.build_search_prompt(query)
        results = self.chroma.query_db(query=search_prompt, k=5, where=db_filter) or {}

        docs_outer = results.get("documents", [[]])
        metas_outer = results.get("metadatas", [[]])

        # Chroma: documents/metadatas are nested lists -> take first inner list
        docs = docs_outer[0] if docs_outer else []
        metas = metas_outer[0] if metas_outer else []

        # 2) Build snippets and citation map
        snippets = []
        citation_map = OrderedDict()

        for doc, meta in zip(docs, metas):
            # meta is a dict here
            title = meta.get("title") or "Untitled"
            year = meta.get("year") or ""
            pdf_path = meta.get("pdf_path") or ""
            key = (title, year, pdf_path)

            if key not in citation_map:
                citation_map[key] = len(citation_map) + 1  # 1-based index

            cid = citation_map[key]
            snippet_text = (doc or "")[:500]  # give the LLM a bit more context
            snippets.append({
                "citation_id": cid,
                "snippet": snippet_text,
                "title": title,
                "year": year,
                "pdf_path": pdf_path,
            })

        citations = [
            {
                "id": cid,
                "title": title,
                "year": year,
                "pdf_path": pdf_path,
            }
            for (title, year, pdf_path), cid in citation_map.items()
        ]

        # 3) Call Ollama to synthesize a nice answer
        prompt = self.build_answer_prompt(query, snippets)
        try:
            summary = generate_answer(prompt)
        except Exception:
            if snippets:
                summary = snippets[0]["snippet"]
            else:
                summary = "No relevant passages found in your Zotero library."

        return {
            "summary": summary,
            "citations": citations,
            "snippets": snippets,
        }



