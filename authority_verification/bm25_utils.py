import re
import json
import time
import pickle
import string
import numpy as np
import pandas as pd
from pyvi import ViTokenizer
from bm25s.tokenization import Tokenizer

filename = r"D:\Personal Projects\authority_verification-main\data\stopwords.csv"
data = pd.read_csv(filename, sep="\t", encoding='utf-8')
list_stopwords = data['stopwords'].tolist()
single_word_list = []
for word in list_stopwords:
    word = word.split('_')
    if len(word) == 1:
        single_word_list.append(word[0])

def clean_text(text):
    text = re.sub('<.*?>', '', text).strip()
    text = re.sub('(\s)+', r'\1', text)
    text = re.sub(r'[0-9]+', '', text)
    # replace '\n' with ' '
    text = text.replace('\n',' ')
    text = text.replace('\"', '')
    return text

def normalize_text(text):
    listpunctuation = string.punctuation.replace('_', '')
    for i in listpunctuation:
        text = text.replace(i, ' ')
    return text.lower()

def word_segment(sent):
    sent = ViTokenizer.tokenize(sent.encode('utf-8').decode('utf-8'))
    return sent

def word_splitter(sentence: str):
    sentence = ViTokenizer.tokenize(sentence.encode('utf-8').decode('utf-8')).split()
    return sentence

def remove_stopword(text, list_stopwords):
    pre_text = []
    words = text.split()
    for word in words:
        if word not in list_stopwords:
            pre_text.append(word)
    text2 = ' '.join(pre_text)
    return text2

def remove_single_word(text):
    pre_text = []
    words = text.split()
    for word in words:
        if word not in single_word_list:
            pre_text.append(word)
    text2 = ' '.join(pre_text)
    return text2

def all_in_one(content: str):
    # return remove_stopword(normalize_text(word_segment(clean_text(content))))
    return remove_stopword(normalize_text(word_segment(clean_text(content))))

def all_in_one_single_stopword(content: str):
    return remove_single_word(normalize_text(word_segment(clean_text(content))))

def tokenize_one_sentence_non_split(sentence:str):
    return ViTokenizer.tokenize(sentence)

def tokenize_one_sentence(sentence: str):
    tokenized = ViTokenizer.tokenize(sentence)
    return tokenized.split()

def test_splitter():
    return (lambda x: x.split())

def create_json_train():
    csv_path = "D:/Personal Projects/authority_verification/data/corpus.csv"
    df = pd.read_csv(csv_path)
    df['text'] = df['text'].str.replace('\n', ' ')
    df['text'] = df['text'].str.replace('\"', '')
    data = df.set_index('cid')['text'].to_dict()
    with open('corpus.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def create_json_train_list():
    csv_path = r"D:\Personal Projects\authority_verification-main\data\corpus.csv"
    df = pd.read_csv(csv_path)
    corpus_list = df['text'].tolist()
    print(corpus_list[:5])
    with open('corpus_list.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)


def clean_corpus():
    with open('D:/Personal Projects/authority_verification/corpus_list.pkl', 'rb') as f:
        corpus_list = pickle.load(f)
        corpus_len = len(corpus_list)
        for i in range(0, corpus_len):
            corpus_list[i] = all_in_one(corpus_list[i])
    
    with open('D:/Personal Projects/authority_verification/corpus_list_clean.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)

if __name__ == "__main__":
    # retrieve_from_saved_vocab()
    # create_json_train_list()
    pass