from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from hazm import stopwords_list, Normalizer

# Load processed data
cleaned_texts_path = 'processed_data.json'
with open(cleaned_texts_path, 'r', encoding='utf-8') as file:
    cleaned_ndata = json.load(file)

texts = [entry['text'] for entry in cleaned_ndata]
keys = [entry['key'] for entry in cleaned_ndata]
persian_dates = [entry['persian_date'] for entry in cleaned_ndata]
urls = [entry['url'] for entry in cleaned_ndata]

# Persian stop words and TF-IDF setup
persian_stop_words = stopwords_list()
vectorizer = TfidfVectorizer(max_features=50000, max_df=0.85, stop_words=persian_stop_words)
tfidf_matrix = vectorizer.fit_transform(texts)

normalizer = Normalizer()

def clean_text(text):
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    return normalizer.normalize(text)

def search_tfidf(query, top_n=5):
    """
    Search for the most similar texts to the query using cosine similarity.
    """
    query = clean_text(query)
    query_vector = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = np.argsort(similarity_scores)[::-1][:top_n]
    return [
        (index, similarity_scores[index], texts[index], keys[index], persian_dates[index], urls[index])
        for index in top_indices
    ]
