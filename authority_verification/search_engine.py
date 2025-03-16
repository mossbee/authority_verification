import re
import json
import math
import pickle
import string
import numpy as np
import pandas as pd
from pyvi import ViTokenizer
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def process_stopwords():
    filename = r"D:\Personal Projects\authority_verification\data\stopwords.csv"
    data = pd.read_csv(filename, sep="\t", encoding='utf-8')
    list_stopwords = data['stopwords'].tolist()
    single_word_list = []
    for word in list_stopwords:
        word = word.split('_')
        if len(word) == 1:
            single_word_list.append(word[0])

def load_stopwords(is_filtered: bool):
    if is_filtered:
        with open('data/stopwords_filtered.pkl', 'rb') as f:
            stopwords = pickle.load(f)
            return stopwords
    else:
        with open('data/stopwords.pkl', 'rb') as f:
            stopwords = pickle.load(f)
            return stopwords

def clean_text(text):
    text = re.sub('<.*?>', '', text).strip()
    text = re.sub('(\s)+', r'\1', text)
    text = re.sub(r'[0-9]+', '', text)
    # replace '\n' with ' '
    text = text.replace('\n',' ')
    text = text.replace('\"', '')
    return text

def word_segment(sent):
    sent = ViTokenizer.tokenize(sent.encode('utf-8').decode('utf-8'))
    return sent

def normalize_text(text):
    listpunctuation = string.punctuation.replace('_', '')
    for i in listpunctuation:
        text = text.replace(i, ' ')
    return text.lower()

def remove_stopword(text, list_stopwords):
    pre_text = []
    words = text.split()
    for word in words:
        if word not in list_stopwords:
            pre_text.append(word)
    text2 = ' '.join(pre_text)
    return text2

def partly_all_in_one(content: str):
    return normalize_text(word_segment(clean_text(content)))

def all_in_one(content: str, list_stopwords):
    return remove_stopword(normalize_text(word_segment(clean_text(content))), list_stopwords)

def create_json_train():
    csv_path = "D:/Personal Projects/authority_verification/data/corpus.csv"
    df = pd.read_csv(csv_path)
    df['text'] = df['text'].str.replace('\n', ' ')
    df['text'] = df['text'].str.replace('\"', '')
    data = df.set_index('cid')['text'].to_dict()
    with open('corpus.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def create_train_list():
    csv_path = "data\corpus.csv"
    df = pd.read_csv(csv_path)
    corpus_list = df['text'].tolist()
    print(corpus_list[:5])
    with open('data\corpus_list.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)

def clean_corpus():
    with open('D:/Personal Projects/authority_verification/corpus_list.pkl', 'rb') as f:
        corpus_list = pickle.load(f)
        corpus_len = len(corpus_list)
        for i in range(0, corpus_len):
            corpus_list[i] = all_in_one(corpus_list[i])
    
    with open('D:/Personal Projects/authority_verification/corpus_list_clean.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)

def process_and_save_idf():
    with open('data\corpus_list.pkl', 'rb') as f:
        huge_corpus = pickle.load(f)
    
    stopwords = load_stopwords(is_filtered=True)
    
    df = {}
    processed_docs = []
    for doc in huge_corpus:
        tokens = partly_all_in_one(doc).split()
        filtered_tokens = [token for token in tokens if token not in stopwords]
        processed_doc = ' '.join(filtered_tokens)
        processed_docs.append(processed_doc)

        for token in set(filtered_tokens):
            df[token] = df.get(token, 0) + 1

    N = len(processed_docs)
    idf = {token: math.log((N + 1) / (freq + 1)) + 1 for token, freq in df.items()}  # Smoothed IDF

    with open('data/idf.pkl', 'wb') as f:
        pickle.dump(idf, f)

def preprocess(text):
    return partly_all_in_one(text).split()
    
def compute_tf(tokens):
    tf = Counter(tokens)
    total_terms = len(tokens)
    return {term: tf[term] / total_terms for term in tf}

def compute_tf_idf(tokens, idf_values):
    tf = compute_tf(tokens)
    tf_idf = {}
    for term, tf_value in tf.items():
        idf_value = idf_values.get(term, 0)  # Use 0 if term not in huge corpus
        tf_idf[term] = tf_value * idf_value
    return tf_idf

def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([v**2 for v in vec1.values()])
    sum2 = sum([v**2 for v in vec2.values()])
    denominator = np.sqrt(sum1) * np.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

# Step 4: Search and Rank Documents
def search(query, small_corpus):
    with open('data/idf.pkl', 'rb') as f:
        idf_values = pickle.load(f)
    
    query_tokens = preprocess(query)
    query_vector = compute_tf_idf(query_tokens, idf_values)
    print(query_vector)

    scores = []
    for doc in small_corpus:
        doc_tokens = preprocess(doc)
        doc_vector = compute_tf_idf(doc_tokens, idf_values)
        print(doc_vector)
        score = cosine_similarity(query_vector, doc_vector)
        scores.append((score, doc))
    
    # Sort by score in descending order
    ranked_results = sorted(scores, key=lambda x: x[0], reverse=True)
    return ranked_results

if __name__ == "__main__":
    small_corpus = [
    "kinh doanh có điều kiện",
    "quy định điều kiện kinh doanh",
    "sửa lốp xe",
    "xe hơi"
]
    query = "kinh doanh dịch vụ đào tạo, bồi dưỡng kiến thức về môi giới bất động sản, định giá bất động sản, quản lý điều hành sàn giao dịch bất động sản là ngành nghề kinh doanh có điều kiện"

    ranked_docs = search(query, small_corpus)
    print("\nRanked Documents:")
    for score, doc in ranked_docs:
        print(f"Score: {score:.4f}, Document: {doc}")