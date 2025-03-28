import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils, doc_utils, knowledge_graph_handler

def get_inspect_and_pursuant_documents():
    for case_folder in os.listdir(config.LEGAL_CASES_PATH):
        # if case_folder is a folder
        case_folder_path = os.path.join(config.LEGAL_CASES_PATH, case_folder)
        if os.path.isdir(case_folder_path):
            # if there is a folder name f"{case_folder}_output" in case_folder_path
            output_folder_path = os.path.join(case_folder_path, f"{case_folder}_output")
            if not os.path.exists(output_folder_path):
                os.mkdir(output_folder_path)  # create the folder
            # if there is a .json file name f'case_{case_folder}.json' in case_folder_path
            case_infor_file_path = os.path.join(case_folder_path, f"case_{case_folder}.json")
            if os.path.exists(case_infor_file_path):
                with open(case_infor_file_path) as f:
                    case = json.load(f)
                    inspect_path = os.path.join(case_folder_path, case['inspection_document']) + '.docx'
                    print("Inspecting document: ", case['inspection_document'] + ".docx")
                    utils.index_one_documents(inspect_path, output_folder_path)
                    utils.index_only_articles_name(inspect_path, output_folder_path)
                    utils.index_full_articles(inspect_path, output_folder_path)
                    utils.index_only_clauses_name(inspect_path, output_folder_path)
                    utils.index_full_clauses(inspect_path, output_folder_path)
                    utils.index_points(inspect_path, output_folder_path)
                    pursuant_docs = case["pursuant_documents"]
                    for pursuant_doc in pursuant_docs:
                        print("Processing pursuant document: ", pursuant_doc + ".docx")
                        pursuant_doc_path = os.path.join(case_folder_path, pursuant_doc) + '.docx'
                        utils.jurisdict_augmentation(pursuant_doc_path, output_folder_path)

if __name__ == "__main__":
    get_inspect_and_pursuant_documents()
    print("Done!")