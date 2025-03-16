import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils, doc_utils, knowledge_graph_handler

def get_inspect_and_pursuant_documents():
    for case_folder in os.listdir(config.LEGAL_CASES_PATH):
        # if case_folder is a folder
        if os.path.isdir(os.path.join(config.LEGAL_CASES_PATH, case_folder)):
            for case_file in os.listdir(os.path.join(config.LEGAL_CASES_PATH, case_folder)):
                if case_file.endswith('.docx'):
                    case_file_path = os.path.join(config.LEGAL_CASES_PATH, case_folder, case_file)
                    utils.extract_jurisdiction_docs(case_file_path)

if __name__ == "__main__":
    get_inspect_and_pursuant_documents()