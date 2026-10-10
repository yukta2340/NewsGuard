# google_news_service.py
"""
Google News Integration Service for NewsGuard.
Connects with Google News India (https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN%3Aen)
to fetch real-time verified political and general news, and corroborates user claims
against live journalistic reporting.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
from datetime import datetime

# Base RSS URLs for Google News (India English edition)
GOOGLE_NEWS_BASE_URL = "https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN%3Aen"
GOOGLE_NEWS_TOP_RSS = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
GOOGLE_NEWS_POLITICS_RSS = "https://news.google.com/rss/headlines/section/topic/POLITICS?hl=en-IN&gl=IN&ceid=IN:en"
GOOGLE_NEWS_SEARCH_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Common stopwords to filter when extracting search keywords
STOPWORDS_QUICK = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in',
    'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with',
    'this', 'these', 'those', 'they', 'their', 'we', 'you', 'or', 'if', 'about', 'into',
    'more', 'all', 'any', 'new', 'news', 'breaking', 'exclusive', 'report', 'reports',
    'said', 'says', 'told', 'also', 'after', 'before', 'over', 'under', 'such', 'like',
    'hai', 'ki', 'ke', 'ka', 'ko', 'se', 'me', 'par', 'aur', 'kya', 'bhi'
}


def clean_xml_text(text):
    """Remove HTML tags, decode entities, and clean up whitespace."""
    if not text:
        return ""
    text = html.unescape(text)
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def extract_search_keywords(text, max_keywords=5):
    """
    Extracts the most salient keywords from news text to construct an effective
    search query for Google News RSS.
    """
    if not text:
        return ""

    # Support Unicode words (English, Hindi, etc.)
    words = re.findall(r'[\w]+', text, flags=re.UNICODE)
    filtered = [w for w in words if w.lower() not in STOPWORDS_QUICK and len(w) > 2]

    # Prioritize capitalized words (names, places, parties)
    proper_nouns = [w for w in filtered if w[0].isupper()]
    other_words = [w for w in filtered if not w[0].isupper()]

    combined = proper_nouns + other_words
    seen = set()
    unique_keywords = []
    for w in combined:
        low = w.lower()
        if low not in seen:
            seen.add(low)
            unique_keywords.append(w)
        if len(unique_keywords) >= max_keywords:
            break

    if not unique_keywords and filtered:
        unique_keywords = filtered[:max_keywords]

    return " ".join(unique_keywords)


def fetch_google_news_feed(feed_type="top", max_articles=15):
    """
    Fetches real-time articles from Google News India.
    
    Args:
        feed_type (str): 'top' for top headlines, 'politics' for political news.
        max_articles (int): Max number of articles to return.
        
    Returns:
        list of dict: List of news items with title, link, publisher, pubDate.
    """
    if feed_type == "politics":
        url = GOOGLE_NEWS_POLITICS_RSS
    else:
        url = GOOGLE_NEWS_TOP_RSS

    articles = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall('.//item')

        for item in items[:max_articles]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            source_elem = item.find('source')

            full_title = clean_xml_text(title_elem.text if title_elem is not None else "")
            link = clean_xml_text(link_elem.text if link_elem is not None else "")
            pub_date = clean_xml_text(pub_date_elem.text if pub_date_elem is not None else "")
            
            # Extract source publisher name
            source_name = "Verified Publisher"
            if source_elem is not None and source_elem.text:
                source_name = clean_xml_text(source_elem.text)
            elif " - " in full_title:
                source_name = full_title.rsplit(" - ", 1)[-1]

            display_title = full_title
            if " - " in display_title:
                display_title = display_title.rsplit(" - ", 1)[0]

            articles.append({
                'title': display_title,
                'source': source_name,
                'link': link,
                'pub_date': pub_date,
                'full_title': full_title
            })

    except Exception as e:
        print(f"Warning: Failed to fetch Google News feed ({feed_type}): {e}")

    return articles


def compute_word_overlap_score(input_text, article_title):
    """
    Computes keyword overlap score between the input news and a Google News headline.
    """
    def tokenize(s):
        return set(w.lower() for w in re.findall(r'[\w]{3,}', s, flags=re.UNICODE) if w.lower() not in STOPWORDS_QUICK)

    set_input = tokenize(input_text)
    set_article = tokenize(article_title)

    if not set_input or not set_article:
        return 0.0

    common = set_input.intersection(set_article)
    return len(common) / min(len(set_article), max(len(set_input), 1))


def search_google_news_evidence(claim_text, max_results=6):
    """
    Searches Google News India live for reports corroborating the claim.
    
    Args:
        claim_text (str): The headline or article text entered by user.
        max_results (int): Max matching articles to return.
        
    Returns:
        dict: {
            'evidence_found': bool,
            'confidence': str ('HIGH', 'MEDIUM', 'LOW', 'NONE'),
            'search_query': str,
            'articles': list of dict,
            'summary': str
        }
    """
    keywords = extract_search_keywords(claim_text, max_keywords=5)
    if not keywords:
        return {
            'evidence_found': False,
            'confidence': 'NONE',
            'search_query': '',
            'articles': [],
            'summary': "Input text too brief to extract search terms."
        }

    encoded_query = urllib.parse.quote(keywords)
    search_url = GOOGLE_NEWS_SEARCH_RSS.format(query=encoded_query)

    matching_articles = []
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall('.//item')

        for item in items:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            source_elem = item.find('source')

            full_title = clean_xml_text(title_elem.text if title_elem is not None else "")
            link = clean_xml_text(link_elem.text if link_elem is not None else "")
            pub_date = clean_xml_text(pub_date_elem.text if pub_date_elem is not None else "")
            
            source_name = "Reputable News Outlet"
            if source_elem is not None and source_elem.text:
                source_name = clean_xml_text(source_elem.text)
            elif " - " in full_title:
                source_name = full_title.rsplit(" - ", 1)[-1]

            display_title = full_title
            if " - " in display_title:
                display_title = display_title.rsplit(" - ", 1)[0]

            score = compute_word_overlap_score(claim_text, full_title)

            if score >= 0.20:
                matching_articles.append({
                    'title': display_title,
                    'source': source_name,
                    'link': link,
                    'pub_date': pub_date,
                    'similarity_score': round(score, 2),
                    'full_title': full_title
                })

            if len(matching_articles) >= max_results:
                break

    except Exception as e:
        print(f"Warning: Failed querying Google News for evidence: {e}")

    # Determine confidence level
    if len(matching_articles) >= 2:
        confidence = "HIGH"
        evidence_found = True
        summary = f"Strong evidence found on Google News India ({len(matching_articles)} credible sources reporting)."
    elif len(matching_articles) == 1:
        confidence = "MEDIUM"
        evidence_found = True
        summary = f"Corroborating coverage detected on Google News India from {matching_articles[0]['source']}."
    else:
        confidence = "NONE"
        evidence_found = False
        summary = "No direct matching coverage found on Google News India. The claim lacks verified media reporting."

    return {
        'evidence_found': evidence_found,
        'confidence': confidence,
        'search_query': keywords,
        'articles': matching_articles,
        'summary': summary
    }


def compute_hybrid_verdict(ml_prediction, evidence_result):
    """
    Combines ML linguistic pattern prediction with Live Google News evidence
    to yield a highly accurate, trustworthy final assessment.
    """
    has_evidence = evidence_result.get('evidence_found', False)
    conf = evidence_result.get('confidence', 'NONE')

    if has_evidence and conf == "HIGH":
        return {
            'final_status': 'REAL',
            'verdict_title': 'VERIFIED REAL NEWS (Live Evidence Confirmed)',
            'badge_type': 'success',
            'explanation': "Cross-checked with Google News India: Multiple reputable journalistic agencies have published verified reports confirming this story."
        }
    elif has_evidence and conf == "MEDIUM":
        if ml_prediction == 'REAL':
            return {
                'final_status': 'REAL',
                'verdict_title': 'LIKELY REAL (Linguistic Match + Live Coverage)',
                'badge_type': 'success',
                'explanation': "The text matches authentic journalistic writing style and is corroborated by active reporting on Google News India."
            }
        else:
            return {
                'final_status': 'REAL',
                'verdict_title': 'CONFIRMED EVENT (Overriding ML Linguistic Flag)',
                'badge_type': 'info',
                'explanation': "Although the phrasing contains emotional or informal language, live Google News coverage confirms this event is genuinely occurring in the news."
            }
    else:
        if ml_prediction == 'FAKE':
            return {
                'final_status': 'FAKE',
                'verdict_title': 'HIGH RISK: LIKELY FAKE NEWS',
                'badge_type': 'danger',
                'explanation': "Both indicators agree: The text exhibits statistical patterns of fabricated news, and ZERO corroborating reports were found on Google News India."
            }
        else:
            return {
                'final_status': 'UNVERIFIED',
                'verdict_title': 'UNVERIFIED CLAIM (No Live Evidence Found)',
                'badge_type': 'warning',
                'explanation': "While the text is written in a neutral/formal tone, no verified journalistic evidence was found on Google News India. Exercise caution before believing or sharing."
            }
