import re
import json
import time
import bm25s
import pickle
import string
import pandas as pd
from pyvi import ViTokenizer
from bm25s.tokenization import Tokenizer

filename = "E:/Projects/authority_verification/data/stopwords.csv"
data = pd.read_csv(filename, sep="\t", encoding='utf-8')
list_stopwords = data['stopwords'].tolist()

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

def remove_stopword(text):
    pre_text = []
    words = text.split()
    for word in words:
        if word not in list_stopwords:
            pre_text.append(word)
    text2 = ' '.join(pre_text)
    return text2

def all_in_one(content: str):
    # return remove_stopword(normalize_text(word_segment(clean_text(content))))
    return remove_stopword(normalize_text(word_segment(clean_text(content))))

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
    csv_path = "D:/Personal Projects/authority_verification/data/corpus.csv"
    df = pd.read_csv(csv_path)
    corpus_list = df['text'].tolist()
    print(corpus_list[:5])
    with open('corpus_list.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)

def test():
    start_time = time.time()
    test_text = "........................................................................................................ Điều ... ............................................................................................ ........................................................................................................ Ghi chú: (1) Tên tỉnh, thành phố trực thuộc Trung ương (tên thị xã, thành phố thuộc tỉnh; tên xã, thị trấn). (2) Địa danh (3) Trích yếu nội dung nghị quyết. (4) Các căn cứ khác để ban hành nghị quyết. (5) Nội dung nghị quyết. (6) Chức vụ của người ký, trường hợp Phó Chủ tịch được giao ký thay Chủ tịch thì ghi chữ viết tắt “KT.” vào trước chức vụ Chủ tịch, bên dưới ghi chức vụ của người ký (Phó Chủ tịch). (7) Chữ viết tắt tên đơn vị soạn thảo và số lượng bản lưu (nếu cần). (8) Ký hiệu người đánh máy, nhân bản và số lượng ản phát hành (nếu cần). Mẫu 1.1.2 – Nghị quyết của Hội đồng quản trị NGHỊ QUYẾT ………………….. (5) ………………….. HỘI ĐỒNG QUẢN TRỊ ……. (2)…… Căn cứ ........................................................................................... Căn cứ............................................................................................ ; ....................................................................................................... ; QUYẾT NGHỊ:"
    ans = all_in_one(test_text)
    ans = tokenize_one_sentence_non_split(clean_text(test_text))
    length = time.time() - start_time
    print(ans)
    print(length)
    create_json_train_list()
    print("hello")
    # "223392": "\"Điều 3. Mở tài khoản tiền gửi
    print(test_splitter("điều 3. mở tài khoản tiền gửi"))

def test_2():
    test_te = "Các căn cứ khác để ban hành nghị quyết nghị. quyết(5) Nội dung nghị quyết."
    print(remove_stopword(normalize_text(word_segment(clean_text(test_te)))))

def clean_corpus():
    with open('D:/Personal Projects/authority_verification/corpus_list.pkl', 'rb') as f:
        corpus_list = pickle.load(f)
        corpus_len = len(corpus_list)
        for i in range(0, corpus_len):
            corpus_list[i] = all_in_one(corpus_list[i])
    
    with open('D:/Personal Projects/authority_verification/corpus_list_clean.pkl', 'wb') as f:
        pickle.dump(corpus_list, f)

def corpus_tokenize():
    with open('D:/Personal Projects/authority_verification/corpus_list_clean.pkl', 'rb') as f:
        corpus = pickle.load(f)

    # Pick your favorite stemmer, and pass 
    stemmer = None
    stopwords = None
    splitter = lambda x: x.split() # function or regex pattern
    # Create a tokenizer
    tokenizer = Tokenizer(
        stemmer=stemmer, stopwords=stopwords, splitter=splitter
    )

    corpus_tokens = tokenizer.tokenize(corpus)

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    tokenizer.save_vocab(save_dir="bm25s_very_big_index")
    retriever.save("legal_index_bm25")

def retrieve_from_saved_vocab():
    new_tokenizer = Tokenizer(
        stemmer = None,
        lower = False,
        stopwords = None,
        splitter = lambda x: x.split(),
    )

    query = "Giấy tờ tùy thân"
    query = all_in_one(query)

    new_tokenizer.load_vocab("bm25s_very_big_index")

    query_tokens = new_tokenizer.tokenize(query)
        # Let's see how it's all used
    reloaded_retriever = bm25s.BM25.load("legal_index_bm25", load_corpus=False)

    # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k)
    # results, scores = reloaded_retriever.retrieve(query_tokens, k=2)

    # You can use a different corpus for retrieval, e.g., titles instead of full docs
    titles = [
                "Việc giới thiệu mẫu con dấu, mẫu chữ ký và chức danh của cơ quan, tổ chức lập, công chứng", 
                "Cơ quan có thẩm quyền chứng nhận lãnh sự, hợp pháp hóa lãnh sự và cơ quan ngoại vụ địa phương", 
                "Giấy tờ tùy thân nêu tại điểm b, điểm c khoản 1 các Điều 11, 13, 14, 15 Nghị định bao gồm chứng minh nhân dân", 
                "Khi tiếp nhận hồ sơ đề nghị chứng nhận lãnh sự, hợp pháp hóa lãnh sự, nếu hồ sơ đã đầy đủ và hợp lệ"
              ]
    titles = [all_in_one(title) for title in titles]

    # You can also choose to only return the documents and omit the scores
    results = reloaded_retriever.retrieve(query_tokens, corpus=titles, k=2, return_as="documents")

    # The documents are returned as a numpy array of shape (n_queries, k)
    for i in range(results.shape[1]):
        print(f"Rank {i+1}: {results[0, i]}")

if __name__ == "__main__":
    retrieve_from_saved_vocab()