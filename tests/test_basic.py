import os
import re
import sys
import json
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authority_verification import config, utils, doc_utils, knowledge_graph_handler

# def find_first_sentence_index(text, sentences_list):
#     """
#     Find the index of the first word of the first sentence that appears in the given text.

#     Args:
#         text (str): The input text.
#         sentences_list (list[str]): List of sentences to search for.

#     Returns:
#         int: Index of the first word of the first matching sentence, or -1 if no match is found.
#     """
#     # Split the text into words and store them in a list with their indices
#     text_words = [(word, idx) for idx, word in enumerate(text.split())]

#     # Iterate over the sentences in the list
#     for sentence in sentences_list:
#         # Split the sentence into words
#         sentence_words = sentence.split()

#         # Check if the sentence appears in the text
#         for idx, (text_word, text_idx) in enumerate(text_words):
#             if text_word == sentence_words[0] and \
#                text_words[idx:idx+len(sentence_words)] == [(w, None) for w in sentence_words]:
#                 # If the sentence matches, return the index of the first word
#                 return text_idx

#     # If no match is found, return -1
#     return -1

# Example usage

def find_first_word_index(text, texts_list):
    words = text.split()
    min_index = float('inf')
    
    for phrase in texts_list:
        phrase_words = phrase.split()
        phrase_length = len(phrase_words)
        
        for i in range(len(words) - phrase_length + 1):
            if words[i:i + phrase_length] == phrase_words:
                min_index = min(min_index, i)
                break
    
    # If no phrase is found, return -1
    return min_index if min_index != float('inf') else -1

# Example usage





if __name__ == "__main__":
    # utils.find_ref_all_legal_docs()
    # utils.find_ref_one_document(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs_all(config.TEST_DOCUMENT_PATH)
    # utils.remove_unwanted_docs_all()
    # utils.jurisdict_augmentation(config.TEST_DOCUMENT_PATH)
    # print(doc_utils.juris_extract('Các cơ sở y tế có trách nhiệm tư vấn về phòng, chống HIV/AIDS; phòng chống lây nhiễm chéo theo quy định của Bộ trưởng Bộ Y tế.'))
    # utils.extract_jurisdiction_doc(config.TEST_DOCUMENT_PATH)
    # knowledge_graph_handler.knowledge_graph_construction(config.TEST_DOCUMENT_PATH)
    # utils.index_and_get_articles(config.TEST_DOCUMENT_PATH)  # index all articles in a document
    # utils.index_and_get_clauses(config.TEST_DOCUMENT_PATH)  # index all clauses in a document)
    # utils.index_one_documents(config.TEST_DOCUMENT_PATH)
    # print(doc_utils.is_alnum('cá'))
    text = "I met some guys at the party, Harry Porter, Draco Malfoy, Ron Weasley"
    texts_list = ["Draco Malfoy", "Ron Weasley", "Harry Porter", "Rubeus Hagrid"]

    index = find_first_word_index(text, texts_list)
    print(index)  # Output: 7