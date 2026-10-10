# backend/ml_engine.py
"""
Machine Learning Linguistic Analysis Engine for NewsGuard.
Handles text cleaning, TF-IDF feature extraction, and high-precision classification.
"""

import os
import re
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Base directory for loading saved models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'fake_news_model.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl')

# Initialize NLTK resources safely
def ensure_nltk_resources():
    try:
        nltk.data.find('corpora/wordnet')
        nltk.data.find('corpora/stopwords')
    except Exception:
        nltk.download('wordnet', quiet=True)
        nltk.download('stopwords', quiet=True)

ensure_nltk_resources()

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def clean_text(text: str) -> str:
    """Cleans raw text for machine learning inference."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    cleaned = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return ' '.join(cleaned)


class MLEngine:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()

    def load_models(self):
        """Loads model and vectorizer from disk."""
        if os.path.exists(MODEL_PATH) and os.path.exists(TFIDF_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.vectorizer = joblib.load(TFIDF_PATH)
            except Exception as e:
                print(f"Error loading ML models: {e}")
                self.model = None
                self.vectorizer = None

    def is_ready(self) -> bool:
        return self.model is not None and self.vectorizer is not None

    def analyze_style(self, text: str) -> dict:
        """
        Analyzes linguistic patterns and predicts REAL or FAKE.
        Returns user-friendly editorial tone signals without exposing code or debug tokens.
        """
        if not self.is_ready():
            return {
                'ready': False,
                'prediction': 'REAL',
                'confidence': 50,
                'tone_assessment': 'Standard Tone'
            }

        cleaned = clean_text(text)
        if not cleaned:
            return {
                'ready': True,
                'prediction': 'REAL',
                'confidence': 50,
                'tone_assessment': 'Neutral Expression'
            }

        vectorized = self.vectorizer.transform([cleaned])
        prediction = self.model.predict(vectorized)[0]

        # Calculate calibrated probability
        confidence = 80
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(vectorized)[0]
            classes = list(self.model.classes_)
            idx = classes.index(prediction)
            confidence = int(round(proba[idx] * 100))
        elif hasattr(self.model, 'decision_function'):
            df_score = abs(float(self.model.decision_function(vectorized)[0]))
            confidence = min(99, int(50 + df_score * 25))

        if prediction == 'REAL':
            tone = "Neutral, objective reporting language with standard journalistic attribution."
        else:
            tone = "Sensational or emotional phrasing commonly identified in unverified or fabricated claims."

        return {
            'ready': True,
            'prediction': prediction,
            'confidence': confidence,
            'tone_assessment': tone
        }
