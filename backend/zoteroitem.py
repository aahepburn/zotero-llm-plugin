import fitz

class ZoteroItem:
    def __init__(self, filepath, metadata=None):
        self.filepath = filepath
        self.metadata = metadata or {}  # allow passing dict for richer info

    def get_title(self):
        # Try to get title from metadata dict first
        if "title" in self.metadata:
            return self.metadata["title"]
        # Fallback: Try extracting from PDF metadata
        try:
            doc = fitz.open(self.filepath)
            title = doc.metadata.get("title")
            doc.close()
            # Remove empty titles, None, etc.
            if title and title.strip():
                return title.strip()
        except Exception as e:
            print(f"Metadata extraction error: {e}")
        return "Untitled"

    def get_author(self):
        if "author" in self.metadata:
            return self.metadata["author"]
        try:
            doc = fitz.open(self.filepath)
            author = doc.metadata.get("author")
            doc.close()
            if author and author.strip():
                return author.strip()
        except Exception as e:
            print(f"Metadata extraction error: {e}")
        return "Unknown author"

    def get_reviews(self):
        # Placeholder: Implement review lookup later (requires more context)
        # Return a default message for MVP
        if self.metadata.get("type") == "book":
            return "Book reviews feature coming soon."
        return "Reviews not available for this item type."

    # Optional for MVP: Simple representation
    def __repr__(self):
        return f"<ZoteroItem: {self.get_title()} by {self.get_author()}>"
