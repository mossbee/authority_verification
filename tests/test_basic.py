import os
import sys
import json
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import python_docx, config, utils, docx_handler

def index_document():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.save_index()

def index_one_document_path(document_path: str):
    document_handler = python_docx.DocumentHandler(document_path)
    document_handler.save_index()

def find_agencies():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.find_agencies()

def find_jurisdictions():
    document_handler = python_docx.DocumentHandler(config.PURSUANT_DOCUMENT_PATH)
    document_handler.save_jurisdict()

def index_all_documents():
    for legal_doc in tqdm(os.listdir(config.LEGAL_DOCS_PATH)):
        dochandler = docx_handler.DocxHandler(config.LEGAL_DOCS_PATH + '/' + legal_doc)
        dochandler.read_docx()
        dochandler.index_document()
        dochandler.save_indexed_paragraphs_to_json()

def find_ref():
    for legal_doc_indexed in tqdm(os.listdir(config.OUTPUT_PATH)):
        if legal_doc_indexed.endswith('_indexed.json'):
            doc_dict = utils.load_json(config.OUTPUT_PATH + legal_doc_indexed)
            output = {}
            for key, value in doc_dict.items():
                ref_list = utils.extract_reference_from_txt(value, key)
                if ref_list:
                    output[key] = ref_list
                else:
                    output[key] = []
            with open(config.OUTPUT_PATH + legal_doc_indexed[:-5] + '_ref.json', 'w', encoding="utf-8") as json_file:
                json_file.write(json.dumps(output, indent = 4, ensure_ascii = False))

if __name__ == "__main__":
    find_ref()