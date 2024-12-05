import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import python_docx, config, utils

def index_document():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.save_index()

def find_agencies():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.find_agencies()

def find_jurisdictions():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.save_jurisdict()

if __name__ == "__main__":
    # index_document()
    find_jurisdictions()