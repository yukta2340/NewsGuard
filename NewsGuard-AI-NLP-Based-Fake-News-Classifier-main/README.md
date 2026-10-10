# 📰 NewsGuard AI – Fake News Detector & Google News Verifier

> **Detect misinformation instantly with Machine Learning and Live Evidence from Google News India.**

---

## 🚀 Live Google News Integration

This system is directly linked to **[Google News India](https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN%3Aen)** (`news.google.com`).

Unlike traditional models that only evaluate wording patterns, **NewsGuard AI** pairs NLP linguistic classification with **real-time journalistic fact-checking** across verified national and global publishers (The Hindu, Indian Express, NDTV, BBC, Reuters, PTI, etc.).

---

## ✨ Key Features

- 🌐 **Connected to Google News India** – Live RSS integration with `https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN%3Aen`
- 🏛️ **Live Political & Top News Explorer** – Browse real-time verified political articles with direct citations and publisher evidence
- ⚡ **Dual-Engine Hybrid Verification** – Combines Passive-Aggressive NLP classification with live media corroboration for higher accuracy
- 🔍 **Real-Time Cross-Checking** – Automatically extracts keywords from user claims and searches Google News for evidence
- 🎯 **One-Click Story Analysis** – Inspect any breaking headline directly from the live feed
- 🎨 **Modern Dark UI** – Built with Streamlit, custom CSS, responsive layout, and distinct visual feedback

---

## 🧠 How It Works: The Dual-Engine Architecture

```
User News Input
      │
      ├───► [NLP Preprocessing & TF-IDF] ───► [Passive-Aggressive Model] ───► Stylistic Label (REAL/FAKE)
      │                                                                                  │
      └───► [Keyword Extraction] ──────────► [Google News India RSS Search] ───► Live Evidence Articles
                                                                                         │
                                                                                         ▼
                                                                           [Hybrid Accuracy Verdict]
```

### 1. 🧼 **Text Preprocessing & ML Classifier**
- Cleans raw input (lowercasing, punctuation removal, NLTK stopword filtering, lemmatization).
- Transforms text using **5,000 TF-IDF features**.
- Evaluates linguistic tone using a **Passive Aggressive Classifier**.

### 2. 🌐 **Live Google News Corroboration**
- Connects to Google News India (`https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN%3Aen`).
- Searches for active journalistic reporting matching the claims and political entities.
- If verified news organizations are reporting the story, it provides evidence links and confirms the event is real.

### 3. 🎯 **Decision Matrix**
| ML Stylistic Prediction | Google News Live Evidence | Hybrid Result |
| :--- | :--- | :--- |
| **REAL** (Objective style) | **HIGH** (Multiple verified sources) | 🟢 **VERIFIED REAL NEWS** |
| **FAKE** (Sensational style) | **HIGH** (Multiple verified sources) | 🟢 **CONFIRMED EVENT** (Evidence overrides style) |
| **REAL** (Objective style) | **NONE** (Zero reports found) | 🟡 **UNVERIFIED CLAIM** (Lacks evidence) |
| **FAKE** (Sensational style) | **NONE** (Zero reports found) | 🔴 **HIGH RISK: FAKE NEWS** |

---

## 🛠️ Tech Stack

- **Python 3.x**
- **Streamlit** – Web application UI
- **Google News India RSS** – Real-time journalistic verification
- **scikit-learn** – Machine Learning (Passive Aggressive Classifier)
- **nltk** – Natural Language Processing
- **pandas** – Data wrangling
- **joblib** – Model persistence

---

## 🧪 Run Locally

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/NewsGuard-Fake-News-Detector.git
cd NewsGuard-Fake-News-Detector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK datasets
python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords')"

# 4. Train model (if models are not present)
python main.py

# 5. Launch the Streamlit application
streamlit run app.py
```

---

## 👨‍💻 Author

**Vinay Meena**  
GitHub: [VinayM1](https://github.com/VinayM1)  
LinkedIn: https://www.linkedin.com/in/vinay-meena-036119326/
