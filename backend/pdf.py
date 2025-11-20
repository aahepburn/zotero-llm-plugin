import fitz

class PDF:
    def __init__(self, filepath):
        self.filepath = filepath
        self.doc = None

    def open(self):
        self.doc = fitz.open(self.filepath)

    def extract_text(self, max_chars=2000):
        self.doc = fitz.open(self.filepath)
        text = ""

        for page in self.doc:
            text += page.get_text()
            if len(text) >= max_chars:
                break
        self.doc.close()

        text = text.replace('\n', "")
        text = text.replace('\t', "")

        return text[:max_chars]
    
    def num_pages(self):
        self.doc = fitz.open(self.filepath)
        count = len(self.doc)
        self.doc.close()
        return count

    def extract_text_by_page(self, page_number):
        self.doc = fitz.open(self.filepath)
        text = self.doc[page_number].get_text()
        self.doc.close()
        return text
    
    def get_metadata(self):
        self.doc = fitz.open(self.filepath)
        metadata = self.doc.metadata
        self.doc.close()
        return metadata  # return a dict
    
    def extract_all_text(self):
        """Retrieves all the text of the PDF by page. stored by page too."""
        self.doc = fitz.open(self.filepath)
        text_chunks = [page.get_text() for page in self.doc]
        self.doc.close()
        return text_chunks  # list of strings, one per page
    
    def get_annotations(self):
        self.doc = fitz.open(self.filepath)
        annots = []
        for page in self.doc:
            for annot in page.annots():
                annots.append(annot.info)
        self.doc.close()
        return annots  # list of annotation dicts







