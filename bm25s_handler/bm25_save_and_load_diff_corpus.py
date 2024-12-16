import bm25s
reloaded_retriever = bm25s.BM25.load("animal_index_bm25", load_corpus=False)

query = "can the cat swims and lives in water"
query_tokens = bm25s.tokenize(query, stemmer=None)

titles = [
    "a cat is a feline and likes to purr",
    "a dog is the human's best friend and loves to play",
    "a bird is a beautiful animal that can fly",
    "a fish is a creature that lives in water and swims",
]

results, scores = reloaded_retriever.retrieve(query_tokens, corpus=titles, k=2)

for i in range(results.shape[1]):
    doc, score = results[0, i], scores[0, i]
    print(f"Rank {i+1} (score: {score:.2f}): {doc}")