import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import python_docx, config

def index_document():
    document_handler = python_docx.DocumentHandler(config.CASE_DOCUMENT_PATH)
    document_handler.save_index()

if __name__ == "__main__":
    index_document()