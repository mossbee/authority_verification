import os
import sys
import json
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils, doc_utils, knowledge_graph_handler

if __name__ == "__main__":
    # utils.find_ref_all_legal_docs()
    # utils.find_ref_one_document(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs_all(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs_all()
    # utils.jurisdict_augmentation(config.TEST_DOCUMENT_PATH)
    # print(doc_utils.juris_extract('Các cơ sở y tế có trách nhiệm tư vấn về phòng, chống HIV/AIDS; phòng chống lây nhiễm chéo theo quy định của Bộ trưởng Bộ Y tế.'))
    # utils.extract_jurisdiction_docs(config.TEST_DOCUMENT_PATH)
    knowledge_graph_handler.knowledge_graph_construction(config.TEST_DOCUMENT_PATH)