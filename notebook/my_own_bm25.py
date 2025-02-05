import json
import math
import pickle
import concurrent
from collections import defaultdict, Counter
from bm25_utils import all_in_one_without_stopword

class BM25Index:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths = []
        self.doc_frequency = defaultdict(int)
        self.inverted_index = defaultdict(list)
        self.total_documents = 0
        self.average_doc_length = 0.0

    def index_corpus(self, corpus):
        """
        Indexes the given corpus (list of documents).
        Each document is a string of space-separated words.
        """
        self.total_documents = len(corpus)

        for doc_id, document in enumerate(corpus):
            tokens = document.split()
            doc_length = len(tokens)
            self.doc_lengths.append(doc_length)
            term_counts = Counter(tokens)

            for term, count in term_counts.items():
                if doc_id not in self.inverted_index[term]:
                    self.inverted_index[term].append((doc_id, count))
                self.doc_frequency[term] += 1

        self.average_doc_length = sum(self.doc_lengths) / self.total_documents

    def save_index(self, filepath):
        """Save the index to a file."""
        with open(filepath, 'w') as f:
            json.dump({
                'inverted_index': {term: postings for term, postings in self.inverted_index.items()},
                'doc_frequency': self.doc_frequency,
                'doc_lengths': self.doc_lengths,
                'total_documents': self.total_documents,
                'average_doc_length': self.average_doc_length,
            }, f)

    def load_index(self, filepath):
        """Load the index from a file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.inverted_index = defaultdict(list, data['inverted_index'])
            self.doc_frequency = defaultdict(int, data['doc_frequency'])
            self.doc_lengths = data['doc_lengths']
            self.total_documents = data['total_documents']
            self.average_doc_length = data['average_doc_length']

    def compute_bm25_score(self, query, doc_id):
        """Compute the BM25 score for a single document and query."""
        score = 0
        query_terms = query.split()

        for term in query_terms:
            if term in self.inverted_index:
                freq = next((count for doc, count in self.inverted_index[term] if doc == doc_id), 0)
                df = self.doc_frequency[term]
                idf = math.log((self.total_documents - df + 0.5) / (df + 0.5) + 1)

                doc_length = self.doc_lengths[doc_id]
                term_score = idf * ((freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * doc_length / self.average_doc_length)))
                score += term_score

        return score

    def query(self, query):
        """Query the index with a string of space-separated words."""
        scores = []
        for doc_id in range(self.total_documents):
            score = self.compute_bm25_score(query, doc_id)
            scores.append((doc_id, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)

# Example usage:
if __name__ == "__main__":
    # Step 1: Indexing a large corpus
    corpus = pickle.load(open('corpus_list.pkl', 'rb'))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        corpus = list(executor.map(all_in_one_without_stopword, corpus))
    
    with open('corpus_list_clean.pkl', 'wb') as f:
        pickle.dump(corpus, f)

    # indexer = BM25Index()
    # indexer.index_corpus(corpus)
    # indexer.save_index("bm25_index.json")

    # # Step 2: Querying with a different corpus
    # query_corpus = [
    #     "bm25 retrieval example",
    #     "sample text that was not indexed"
    # ]

    # indexer.load_index("bm25_index.json")
    # for i, query in enumerate(query_corpus):
    #     results = indexer.query(query)
    #     print(f"Query {i+1}: {query}")
    #     for doc_id, score in results:
    #         print(f"  Document {doc_id}: Score {score}")
