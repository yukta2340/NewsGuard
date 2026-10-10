# predictor.py
# This file contains the logic for making predictions on new news texts,
# enhanced with Google News India real-time cross-checking.

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import google_news_service as gns

# Initialize lemmatizer and stop words globally for efficiency
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text_single(text):
    """
    This function cleans up a single piece of news text for predictor.py's use.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)

    words = text.split()

    cleaned_words = [
        lemmatizer.lemmatize(word) for word in words if word not in stop_words
    ]

    return ' '.join(cleaned_words)


def predict_news(text, tfidf_vectorizer, model, check_live_evidence=True):
    """
    This function takes a brand new piece of news and tells us if it's real or fake,
    cross-referencing with Google News India for real-time evidence.
    """
    print(f"\n--- Predicting for new text ---")
    print(f"Original text: '{text[:100]}...'")

    # 1. Clean the new text
    cleaned_text = clean_text_single(text)

    # 2. Convert the cleaned text into numbers using the SAME TF-IDF tool
    text_vectorized = tfidf_vectorizer.transform([cleaned_text])

    # 3. Make a prediction using our trained model
    ml_prediction = model.predict(text_vectorized)[0]
    print(f"ML Model Linguistic Prediction: '{ml_prediction}'")

    # 4. Optional Live Google News cross-checking
    if check_live_evidence:
        print("Checking Google News India (https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en)...")
        evidence = gns.search_google_news_evidence(text, max_results=3)
        hybrid = gns.compute_hybrid_verdict(ml_prediction, evidence)
        print(f"Google News Evidence Found: {evidence['evidence_found']} (Confidence: {evidence['confidence']})")
        if evidence['articles']:
            print("Corroborating Sources:")
            for art in evidence['articles']:
                print(f"  - [{art['source']}] {art['title']}")
        print(f"Final Hybrid Verdict: {hybrid['verdict_title']}")
        return hybrid['final_status']

    return ml_prediction
