import bm25s
from bm25s.tokenization import Tokenizer
from bm25_utils import all_in_one

corpus = [
    "mèo là loài động vật thuộc họ mèo và thích rên",
    "chó là bạn thân nhất của người và thích chơi",
    "chim là loài động vật đẹp đẽ và biết bay",
    "cá là loài sống trong nước và biết bơi",
]

corpus = [all_in_one(doc) for doc in corpus]

tokenizer = Tokenizer(stemmer=None, stopwords=None, splitter=lambda x: x.split())
corpus_tokens = tokenizer.tokenize(corpus)

retriever = bm25s.BM25()
retriever.index(corpus_tokens)

query = ["loài nào biết bay"]
query = [all_in_one(q) for q in query]
query_tokens = tokenizer.tokenize(query)

titles = [
    "mèo là loài động vật thuộc họ mèo và thích rên",
    "chó là bạn thân nhất của người và thích chơi",
    "chim là loài động vật đẹp đẽ và biết bay",
    "cá là loài sống trong nước và biết bơi",
]
titles = [all_in_one(title) for title in titles]

results, scores = retriever.retrieve(query_tokens, corpus=titles, k=2)

for i in range(results.shape[1]):
    doc, score = results[0, i], scores[0, i]
    print(f"Rank {i+1} (score: {score:.2f}): {doc}")