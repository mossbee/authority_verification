import math
import json
import pickle
import concurrent
import bm25_utils
from collections import defaultdict

corpus = pickle.load(open(r"D:\Personal Projects\authority_verification-main\corpus_list.pkl", "rb"))

with concurrent.futures.ThreadPoolExecutor() as executor:
    corpus = list(executor.map(bm25_utils.all_in_one_single_stopword, corpus))

def index_huge_corpus(huge_corpus):
    df = defaultdict(int)
    total_docs = len(huge_corpus)

    for doc in huge_corpus:
        unique_tokens = set(doc.split())
        for token in unique_tokens:
            df[token] += 1

    idf = {}
    for token, freq in df.items():
        idf[token] = math.log((total_docs + 1) / (freq + 1)) + 1

    return idf

idf = index_huge_corpus(corpus)

with open("idf_single_word.json", "w", encoding="utf-8") as f:
    json.dump(idf, f, ensure_ascii=False, indent=4)