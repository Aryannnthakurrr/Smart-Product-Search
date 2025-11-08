import os
import pickle
import string
from collections import defaultdict
from collections import Counter
from nltk.stem import PorterStemmer
import math

from .search_utils import (
    CACHE_DIR,
    DEFAULT_SEARCH_LIMIT,
    load_movies,
    load_stopwords,
    BM25_K1,
    BM25_B
)


class InvertedIndex:
    def __init__(self) -> None:
        self.index = defaultdict(set)
        self.docmap: dict[int, dict] = {}
        self.term_frequencies = {}
        self.index_path = os.path.join(CACHE_DIR, "index.pkl")
        self.docmap_path = os.path.join(CACHE_DIR, "docmap.pkl")
        self.term_frequency_path = os.path.join(CACHE_DIR, "term_frequencies.pkl")
        self.doc_lengths: dict[int, int] = {}
        self.doc_lengths_path = os.path.join(CACHE_DIR, "doc_lengths.pkl")

    def build(self) -> None:
        movies = load_movies()
        for m in movies:
            doc_id = m["id"]
            doc_description = f"{m['title']} {m['description']}"
            self.docmap[doc_id] = m
            self.__add_document(doc_id, doc_description)

    def save(self) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump(self.index, f)
        with open(self.docmap_path, "wb") as f:
            pickle.dump(self.docmap, f)
        with open(self.term_frequency_path, "wb") as f:
            pickle.dump(self.term_frequencies, f)
        with open(self.doc_lengths_path, "wb") as f:
            pickle.dump(self.doc_lengths, f)

    def load(self) -> None:
        with open(self.index_path, "rb") as f:
            self.index = pickle.load(f)
        with open(self.docmap_path, "rb") as f:
            self.docmap = pickle.load(f)
        with open(self.term_frequency_path, "rb") as f:
            self.term_frequencies = pickle.load(f)
        with open(self.doc_lengths_path, "rb") as f:
            self.doc_lengths = pickle.load(f)

    def get_documents(self, term: str) -> list[int]:
        doc_ids = self.index.get(term, set())
        return sorted(list(doc_ids))
    
    def get_tf(self, doc_id: str, term: str) -> int:
        tokens = tokenize_text(term)
        if len(tokens) != 1:
            raise ValueError("Input term must result in exactly one token after preprocessing.")
        if doc_id not in self.term_frequencies:
            return 0
        
        doc_counter = self.term_frequencies[doc_id]
        return doc_counter.get(tokens[0], 0)

    def get_idf(self, term: str) -> tuple[float, str]:
        tokens = tokenize_text(term)

        if not tokens:
            raise ValueError(f"Term '{term}' is a stopword or invalid.")

        if len(tokens) > 1:
            raise ValueError(f"Please provide a single term. '{term}' tokenized to {tokens}")

        processed_term = tokens[0]
        term_doc_count = len(self.index.get(processed_term, set()))
        doc_count = len(self.docmap)

        idf = math.log((doc_count + 1) / (term_doc_count + 1))

        return idf, processed_term


    def __add_document(self, doc_id: int, text: str) -> None:
        tokens = tokenize_text(text)

        self.doc_lengths[doc_id] = len(tokens)
        for token in set(tokens):
            self.index[token].add(doc_id)
        if doc_id not in self.term_frequencies:
            self.term_frequencies[doc_id] = Counter()
        doc_counter = self.term_frequencies[doc_id]
        for token in tokens:
            if token not in self.index:
                self.index[token] = {doc_id}
            else:
                self.index[token].add(doc_id)

            doc_counter[token]+=1

    def get_bm25_idf(self, term:str)->float:
        tokens = tokenize_text(term)
        if not tokens:
            raise ValueError(f"Term '{term}' is a stopword or invalid.")

        if len(tokens) > 1:
            raise ValueError(f"Please provide a single term. '{term}' tokenized to {tokens}")

        processed_term = tokens[0]
        term_doc_count = len(self.index.get(processed_term, set()))
        doc_count = len(self.docmap)
        bm25_IDF = math.log((doc_count - term_doc_count + 0.5)/(term_doc_count + 0.5) + 1)
        return bm25_IDF

    def get_bm25_tf(self, doc_id:int, term:str, K1:float = BM25_K1, b:float = BM25_B)->float:
        tf = self.get_tf(doc_id, term)
        doc_length = self.doc_lengths.get(doc_id,0)
        avg_doc_length = self.__get_avg_doc_length()
        length_norm = 1 - b + b * (doc_length / avg_doc_length)
        if avg_doc_length == 0:
            length_norm = 1.0
        bm25_tf = (tf * (K1+1)) / (tf+K1 * length_norm)
        return bm25_tf

    def __get_avg_doc_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        total_length = sum(self.doc_lengths.values())
        avg_length = total_length / len(self.doc_lengths)
        return avg_length

    def bm25(self, doc_id, term):
        bm25_tf = self.get_bm25_tf(doc_id, term)
        bm25_idf = self.get_bm25_idf(term)
        BM25_score = bm25_tf * bm25_idf
        return BM25_score
     
    def bm25_search(self, query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
        query_tokens = tokenize_text(query)
    
        if not query_tokens:
            return []
    
        # Initialize a scores dictionary to map document IDs to their total BM25 scores
        scores: dict[int, float] = {}
    
        # For each document in the index, calculate the total BM25 score
        for doc_id in self.docmap.keys():
            total_score = 0.0
        
            # For each query token, add its BM25 score to the document's running total
            for query_token in query_tokens:
                bm25_score = self.bm25(doc_id, query_token)
                total_score += bm25_score
        
            # Store the total score in the scores dictionary
            scores[doc_id] = total_score
    
        # Sort the documents by score in descending order
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
        # Return the top limit documents along with their scores
        results = []
        for doc_id, score in sorted_docs[:limit]:
            doc = self.docmap[doc_id].copy()
            doc["bm25_score"] = score
            results.append(doc)
    
        return results
        

def bm25_idf_command(term)->float:
    idx = InvertedIndex()
    idx.load()
    bm25_idf = idx.get_bm25_idf(term)
    return bm25_idf

def bm25_tf_command(doc_id, term, K1:float = BM25_K1, b:float = BM25_B):
    idx = InvertedIndex()
    idx.load()
    bm25_tf = idx.get_bm25_tf(doc_id, term, K1, b)
    return bm25_tf


def build_command() -> None:
    idx = InvertedIndex()
    idx.build()
    idx.save()

def search_command(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
    idx = InvertedIndex()
    idx.load()
    query_tokens = tokenize_text(query)
    seen, results = set(), []
    for query_token in query_tokens:
        matching_doc_ids = idx.get_documents(query_token)
        for doc_id in matching_doc_ids:
            if doc_id in seen:
                continue
            seen.add(doc_id)
            doc = idx.docmap[doc_id]
            if not doc:
                continue
            results.append(doc)
            if len(results) >= limit:
                return results

    return results

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


def tokenize_text(text: str) -> list[str]:
    text = preprocess_text(text)
    tokens = text.split()
    valid_tokens = []
    for token in tokens:
        if token:
            valid_tokens.append(token)
    stop_words = load_stopwords()
    filtered_words = []
    for word in valid_tokens:
        if word not in stop_words:
            filtered_words.append(word)
    stemmer = PorterStemmer()
    stemmed_words = []
    for word in filtered_words:
        stemmed_words.append(stemmer.stem(word))
    return stemmed_words
