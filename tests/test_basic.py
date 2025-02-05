import os
import sys
import json
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils

if __name__ == "__main__":
    # utils.find_ref_all_legal_docs()
    # utils.find_ref_one_document(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs(config.TEST_DOCUMENT_PATH)
    utils.document_augmentation(config.TEST_DOCUMENT_PATH, is_save_index=True, is_save_ref=True, is_save_filtered=True)