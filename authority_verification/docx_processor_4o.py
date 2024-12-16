import json
from docx import Document

class DocxHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.document = None
        self.paragraphs_index = {}

    def read_docx_file(self):
        """Reads the .docx file and loads it into the document attribute."""
        self.document = Document(self.file_path)

    def index_paragraphs(self):
        """Indexes the paragraphs in the document and stores them in a dictionary."""
        if self.document is None:
            raise ValueError("Document not loaded. Please read the .docx file first.")
        
        self.paragraphs_index = {i: para.text for i, para in enumerate(self.document.paragraphs)}

    def save_indexed_paragraphs_to_json(self, output_file_path):
        """Saves the indexed paragraphs to a .json file."""
        if not self.paragraphs_index:
            raise ValueError("No paragraphs indexed. Please index the paragraphs first.")
        
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.paragraphs_index, json_file, ensure_ascii=False, indent=4)

# Example usage:
if __name__ == "__main__":
    docx_handler = DocxHandler("example.docx")
    docx_handler.read_docx_file()
    docx_handler.index_paragraphs()
    docx_handler.save_indexed_paragraphs_to_json("indexed_paragraphs.json")