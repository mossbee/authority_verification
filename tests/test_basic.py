import os
import sys
import json
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils, doc_utils

if __name__ == "__main__":
    # utils.find_ref_all_legal_docs()
    # utils.find_ref_one_document(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs(config.TEST_DOCUMENT_PATH)
    # utils.document_augmentation(config.TEST_DOCUMENT_PATH, is_save_index=True, is_save_ref=True, is_save_filtered=True)
    print(doc_utils.juris_extract('Mặt trận Tổ quốc Việt Nam và các tổ chức thành viên có trách nhiệm tuyên truyền, vận động nhân dân tham gia phòng, chống HIV/AIDS; tham gia và giám sát thực hiện biện pháp phòng, chống HIV/AIDS; tổ chức, thực hiện phong trào hỗ trợ về vật chất, tinh thần đối với người nhiễm HIV.'))