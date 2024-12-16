import bm25s
from bm25s.tokenization import Tokenizer, Tokenized
from bm25_utils import all_in_one

corpus = [
    "mèo là loài động vật thuộc họ mèo và thích rên",
    "chó là bạn thân nhất của người và thích chơi",
    "chim là loài động vật đẹp đẽ và biết bay",
    "cá là loài sống trong nước và biết bơi",
]

corpus = [all_in_one(doc) for doc in corpus]

print(corpus)

tokenizer = Tokenizer(stemmer=None, stopwords=None, splitter=lambda x: x.split())
corpus_tokens = tokenizer.tokenize(corpus)
print("tokens:", corpus_tokens)
print("type", type(corpus_tokens))
print("vocab:", tokenizer.get_vocab_dict())
tokenized = Tokenized(ids=corpus_tokens, vocab=tokenizer.get_vocab_dict())


retriever = bm25s.BM25()
retriever.index(tokenized)

retriever.save("animal_index_bm25_vietnam")
print(f"{retriever.vocab_dict=}")
tokenizer.save_vocab(save_dir="animal_index_bm25_vietnam")

query = ["loài nào biết bay"]
query = [all_in_one(q) for q in query]
print(query)
query_tokens = tokenizer.tokenize(query)
print("query tokens:", query_tokens)


results, scores = retriever.retrieve(query_tokens, k=2)

for i in range(results.shape[1]):
    doc, score = results[0, i], scores[0, i]
    print(f"Rank {i+1} (score: {score:.2f}): {doc}")
