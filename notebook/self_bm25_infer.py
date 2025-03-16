import json
import bm25_utils
from typing import Dict
from collections import defaultdict

def bm25_score(query, document, idf, k1=1.5, b=0.75, avg_doc_len=None):
    """
    Compute BM25 score between a query and a document.
    """
    query_tokens = query.split()
    doc_tokens = document.split()

    doc_len = len(doc_tokens)
    if avg_doc_len is None:
        avg_doc_len = doc_len

    tf = defaultdict(int)
    for token in doc_tokens:
        tf[token] += 1

    score = 0.0
    for token in query_tokens:
        if token in idf:
            numerator = tf[token] * (k1 + 1)
            denominator = tf[token] + k1 * (1 - b + b * (doc_len / avg_doc_len))
            score += idf[token] * (numerator / denominator)

    return score

def query_smaller_corpus(smaller_corpus, query, idf):
    # Calculate average document length for BM25 normalization
    doc_lengths = [len(doc.split()) for doc in smaller_corpus]
    avg_doc_len = sum(doc_lengths) / len(smaller_corpus)

    # Filter tokens in the query and smaller corpus based on the huge corpus IDF
    filtered_query = " ".join([token for token in query.split() if token in idf])
    filtered_corpus = [
        " ".join([token for token in doc.split() if token in idf])
        for doc in smaller_corpus
    ]

    # Compute BM25 scores
    scores = []
    for doc in filtered_corpus:
        score = bm25_score(filtered_query, doc, idf, avg_doc_len=avg_doc_len)
        scores.append(score)

    # Sort documents by their BM25 scores
    sorted_docs = sorted(
        zip(smaller_corpus, scores), key=lambda x: x[1], reverse=True
    )

    return sorted_docs

def query_smaller_corpus_as_dict(smaller_corpus: Dict, query, idf):
    # Calculate average document length for BM25 normalization
    doc_lengths = [len(doc.split()) for doc in smaller_corpus.values()]
    avg_doc_len = sum(doc_lengths) / len(smaller_corpus)

    # Filter tokens in the query and smaller corpus based on the huge corpus IDF
    filtered_query = " ".join([token for token in query.split() if token in idf])
    filtered_corpus = [
        " ".join([token for token in doc.split() if token in idf])
        for doc in smaller_corpus.values()
    ]

    # Compute BM25 scores
    scores = []
    for doc in filtered_corpus:
        score = bm25_score(filtered_query, doc, idf, avg_doc_len=avg_doc_len)
        scores.append(score)

    # Sort documents by their BM25 scores
    sorted_docs = sorted(
        zip(list(smaller_corpus.values()), scores, list(smaller_corpus.keys())), key=lambda x: x[1], reverse=True
    )

    return sorted_docs

# Example usage
smaller_corpus = [
    "kinh doanh có điều kiện",
    "quy định điều kiện kinh doanh",
    "sửa lốp xe",
    "xe hơi"
]

smaller_corpus = list(json.load(open('data/output/67_2014_QH13_259729_indexed_augmented_filtered.json', 'r', encoding='utf-8')).values())
smaller_corpus_dict = json.load(open('data/output/67_2014_QH13_259729_indexed_augmented_filtered.json', 'r', encoding='utf-8'))

query = "kinh doanh dịch vụ đào tạo, bồi dưỡng kiến thức về môi giới bất động sản, định giá bất động sản, quản lý điều hành sàn giao dịch bất động sản là ngành nghề kinh doanh có điều kiện"
smaller_corpus = [bm25_utils.all_in_one_single_stopword(doc) for doc in smaller_corpus]
smaller_corpus_dict = {key: bm25_utils.all_in_one_single_stopword(value) for key, value in smaller_corpus_dict.items()}
query = bm25_utils.all_in_one_single_stopword(query)
# print(smaller_corpus)
# print(query)

# Load IDF from the huge corpus
idf = json.load(open('idf_single_word.json', 'r', encoding='utf-8'))

# Get BM25 results
results = query_smaller_corpus_as_dict(smaller_corpus_dict, query, idf)

# Print ranked results
print("Ranked Results:")
for doc, score, index in results:
    if score != 0:
        print(f"Document: {doc[:50]}, Score: {score}, Index: {index}")