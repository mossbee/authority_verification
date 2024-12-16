import bm25s
from bm25s.tokenization import Tokenizer
from bm25_utils import all_in_one

reloaded_retriever = bm25s.BM25.load("animal_index_bm25_vietnam", load_corpus=False)
print("retriever reloaded:", reloaded_retriever.vocab_dict)

tokenizer = Tokenizer(stemmer=None, stopwords=None, splitter=lambda x: x.split())
tokenizer.load_vocab("animal_index_bm25_vietnam")
print("vocab reloaded:", tokenizer.get_vocab_dict())

query = ["loài nào biết bay"]
query = [all_in_one(q) for q in query]

query_tokens = tokenizer.tokenize(query, update_vocab=False)
print(query_tokens)

titles = [
    "mèo là loài động vật thuộc họ mèo và thích rên",
    "chó là bạn thân nhất của người và thích chơi",
    "chim là loài động vật đẹp đẽ và biết bay",
    "cá là loài sống trong nước và biết bơi",
]
titles = [all_in_one(title) for title in titles]
print(titles)
titles_tokens = tokenizer.tokenize(titles, update_vocab=False)
print(titles_tokens)
print(tokenizer.get_vocab_dict())

results, scores = reloaded_retriever.retrieve(query_tokens, corpus=titles, k=2)

for i in range(results.shape[1]):
    doc, score = results[0, i], scores[0, i]
    print(f"Rank {i+1} (score: {score:.2f}): {doc}")