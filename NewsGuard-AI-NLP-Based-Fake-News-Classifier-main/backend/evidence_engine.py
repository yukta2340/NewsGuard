# backend/evidence_engine.py
"""
Live Journalistic Evidence Engine for NewsGuard.
Corroborates claims against live press wires and accredited news agencies in real-time,
including NDTV Latest (https://www.ndtv.com/latest) for comprehensive general, national,
sports, entertainment, and world coverage.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html

# Unbranded live press wire endpoints (India English edition)
LIVE_WIRE_TOP_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
LIVE_WIRE_POLITICS_URL = "https://news.google.com/rss/headlines/section/topic/POLITICS?hl=en-IN&gl=IN&ceid=IN:en"
LIVE_WIRE_SEARCH_URL = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

# NDTV Latest live feed endpoint (covers all non-political, national, sports, world, science, lifestyle)
NDTV_LATEST_RSS = "https://feeds.feedburner.com/ndtvnews-latest"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Common stopwords to filter for query extraction
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in',
    'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with',
    'this', 'these', 'those', 'they', 'their', 'we', 'you', 'or', 'if', 'about', 'into',
    'more', 'all', 'any', 'new', 'news', 'breaking', 'exclusive', 'report', 'reports',
    'said', 'says', 'told', 'also', 'after', 'before', 'over', 'under', 'such', 'like',
    'hai', 'ki', 'ke', 'ka', 'ko', 'se', 'me', 'par', 'aur', 'kya', 'bhi'
}

HOAX_KEYWORDS = {
    'alien', 'aliens', 'ufo', 'secret', 'miracle', 'chips', 'conspiracy', 'illuminati',
    'infiltrated', 'android', 'banned', 'immortal', 'invisble', 'pizza currency', 'cure'
}


def clean_xml_string(raw: str) -> str:
    """Decodes HTML entities and strips tags."""
    if not raw:
        return ""
    text = html.unescape(raw)
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def extract_key_entities(text: str, max_terms: int = 5) -> str:
    """Extracts salient entities and nouns for press wire search."""
    if not text:
        return ""
    words = re.findall(r'[\w]+', text, flags=re.UNICODE)
    meaningful = [w for w in words if w.lower() not in STOPWORDS and len(w) > 2]

    # Prioritize capitalized terms (proper nouns, places, organizations)
    proper_nouns = [w for w in meaningful if w[0].isupper()]
    standard_nouns = [w for w in meaningful if not w[0].isupper()]

    combined = proper_nouns + standard_nouns
    seen = set()
    selected = []
    for w in combined:
        low = w.lower()
        if low not in seen:
            seen.add(low)
            selected.append(w)
        if len(selected) >= max_terms:
            break

    if not selected and meaningful:
        selected = meaningful[:max_terms]

    return " ".join(selected)


def compute_relevance_score(claim_text: str, headline: str) -> tuple:
    """
    Calculates coverage of claim keywords in the news headline.
    Returns (score, common_keyword_count).
    """
    def tokenize(s):
        return set(w.lower() for w in re.findall(r'[\w]{3,}', s, flags=re.UNICODE) if w.lower() not in STOPWORDS)

    set_q = tokenize(claim_text)
    set_h = tokenize(headline)

    if not set_q or not set_h:
        return 0.0, 0

    common = set_q.intersection(set_h)
    coverage = len(common) / len(set_q)
    return round(coverage, 2), len(common)


def fetch_ndtv_latest_feed(max_items: int = 15) -> list:
    """
    Fetches real-time general news from NDTV Latest (https://www.ndtv.com/latest),
    covering everything apart from political news: sports, world, science, health,
    crime, entertainment, technology, and weather.
    """
    articles = []
    try:
        req = urllib.request.Request(NDTV_LATEST_RSS, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=6) as res:
            xml_content = res.read()

        root = ET.fromstring(xml_content)
        items = root.findall('.//item')

        for item in items[:max_items]:
            t_node = item.find('title')
            l_node = item.find('link')
            d_node = item.find('pubDate')

            title = clean_xml_string(t_node.text if t_node is not None else "")
            link = clean_xml_string(l_node.text if l_node is not None else "")
            pub_date = clean_xml_string(d_node.text if d_node is not None else "")

            # Strip feedburner tracking query
            if "#publisher=newsstand" in link:
                link = link.replace("#publisher=newsstand", "")

            articles.append({
                'title': title,
                'source': 'NDTV News',
                'link': link,
                'pub_date': pub_date
            })
    except Exception as e:
        print(f"Warning: Failed to fetch NDTV Latest feed: {e}")

    return articles


def fetch_live_press_feed(category: str = "ndtv", max_items: int = 12) -> list:
    """
    Retrieves live articles from accredited journalistic press wires or NDTV Latest.
    """
    if category == "ndtv":
        return fetch_ndtv_latest_feed(max_items=max_items)

    url = LIVE_WIRE_POLITICS_URL if category == "politics" else LIVE_WIRE_TOP_URL
    articles = []

    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=8) as res:
            xml_content = res.read()

        root = ET.fromstring(xml_content)
        items = root.findall('.//item')

        for item in items[:max_items]:
            title_node = item.find('title')
            link_node = item.find('link')
            date_node = item.find('pubDate')
            source_node = item.find('source')

            raw_title = clean_xml_string(title_node.text if title_node is not None else "")
            link = clean_xml_string(link_node.text if link_node is not None else "")
            pub_date = clean_xml_string(date_node.text if date_node is not None else "")

            publisher = "Press Wire"
            if source_node is not None and source_node.text:
                publisher = clean_xml_string(source_node.text)
            elif " - " in raw_title:
                publisher = raw_title.rsplit(" - ", 1)[-1]

            display_title = raw_title
            if " - " in display_title:
                display_title = display_title.rsplit(" - ", 1)[0]

            articles.append({
                'title': display_title,
                'source': publisher,
                'link': link,
                'pub_date': pub_date
            })

    except Exception as e:
        print(f"Warning: Failed to fetch live press feed: {e}")

    return articles


def search_journalistic_evidence(claim_text: str, max_results: int = 5) -> dict:
    """
    Searches live journalistic dispatches and NDTV Latest (https://www.ndtv.com/latest)
    to verify if accredited news organizations are reporting on the claim.
    """
    query_terms = extract_key_entities(claim_text, max_terms=5)
    if not query_terms:
        return {
            'evidence_found': False,
            'confidence': 'NONE',
            'search_query': '',
            'articles': [],
            'summary': "Insufficient context to extract search terms."
        }

    encoded_query = urllib.parse.quote(query_terms)
    search_url = LIVE_WIRE_SEARCH_URL.format(query=encoded_query)
    matches = []
    seen_titles = set()

    # 1. Check live wire search
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=8) as res:
            xml_content = res.read()

        root = ET.fromstring(xml_content)
        items = root.findall('.//item')

        for item in items:
            title_node = item.find('title')
            link_node = item.find('link')
            date_node = item.find('pubDate')
            source_node = item.find('source')

            raw_title = clean_xml_string(title_node.text if title_node is not None else "")
            link = clean_xml_string(link_node.text if link_node is not None else "")
            pub_date = clean_xml_string(date_node.text if date_node is not None else "")

            publisher = "Journalistic Source"
            if source_node is not None and source_node.text:
                publisher = clean_xml_string(source_node.text)
            elif " - " in raw_title:
                publisher = raw_title.rsplit(" - ", 1)[-1]

            display_title = raw_title
            if " - " in display_title:
                display_title = display_title.rsplit(" - ", 1)[0]

            coverage_score, common_count = compute_relevance_score(claim_text, display_title)

            if coverage_score >= 0.40 and common_count >= 2:
                key = display_title.lower()[:35]
                if key not in seen_titles:
                    seen_titles.add(key)
                    matches.append({
                        'title': display_title,
                        'source': publisher,
                        'link': link,
                        'pub_date': pub_date,
                        'relevance_score': coverage_score
                    })

            if len(matches) >= max_results:
                break

    except Exception as e:
        print(f"Warning: Live journalistic search failed: {e}")

    # 2. Check NDTV Latest feed directly (for general/world/sports/non-political stories)
    try:
        ndtv_feed = fetch_ndtv_latest_feed(max_items=35)
        for art in ndtv_feed:
            c_score, c_count = compute_relevance_score(claim_text, art['title'])
            if c_score >= 0.35 and c_count >= 2:
                key = art['title'].lower()[:35]
                if key not in seen_titles:
                    seen_titles.add(key)
                    matches.append({
                        'title': art['title'],
                        'source': 'NDTV News',
                        'link': art['link'],
                        'pub_date': art['pub_date'],
                        'relevance_score': c_score
                    })
            if len(matches) >= max_results:
                break
    except Exception as e:
        print(f"Warning: NDTV scan failed: {e}")

    if len(matches) >= 2:
        confidence = "HIGH"
        evidence_found = True
        summary = f"Confirmed by {len(matches)} accredited journalistic news agencies (including NDTV / national wires)."
    elif len(matches) == 1:
        confidence = "MODERATE"
        evidence_found = True
        summary = f"Corroborating reporting detected from {matches[0]['source']}."
    else:
        confidence = "NONE"
        evidence_found = False
        summary = "No matching reports found across accredited journalistic news agencies."

    return {
        'evidence_found': evidence_found,
        'confidence': confidence,
        'search_query': query_terms,
        'articles': matches,
        'summary': summary
    }


def compute_hybrid_credibility(ml_prediction: str, evidence: dict) -> dict:
    """
    Synthesizes ML linguistic signals with live press wire evidence.
    """
    has_evidence = evidence.get('evidence_found', False)
    conf = evidence.get('confidence', 'NONE')

    if ml_prediction == 'REAL':
        if has_evidence and conf == "HIGH":
            return {
                'status': 'REAL',
                'badge': 'VERIFIED AUTHENTIC',
                'theme': 'emerald',
                'score_percent': 96,
                'headline': 'Verified Genuine Event',
                'detail': 'Corroborated by multiple accredited press agencies reporting active coverage.'
            }
        elif has_evidence and conf == "MODERATE":
            return {
                'status': 'REAL',
                'badge': 'CONFIRMED REPORTING',
                'theme': 'emerald',
                'score_percent': 88,
                'headline': 'Authentic Press Dispatch',
                'detail': 'Corroborated by active reporting from accredited news publishers.'
            }
        else:
            return {
                'status': 'REAL',
                'badge': 'OBJECTIVE REPORTING',
                'theme': 'emerald',
                'score_percent': 78,
                'headline': 'Standard Factual News Tone',
                'detail': 'Written with neutral, professional journalistic attribution.'
            }
    else:
        # ML Prediction is FAKE
        if has_evidence and conf == "HIGH":
            return {
                'status': 'REAL',
                'badge': 'CONFIRMED INCIDENT',
                'theme': 'blue',
                'score_percent': 82,
                'headline': 'Real Incident Reported',
                'detail': 'Despite informal or urgent phrasing, news organizations confirm this event is real.'
            }
        else:
            return {
                'status': 'FAKE',
                'badge': 'MISINFORMATION ALERT',
                'theme': 'rose',
                'score_percent': 14,
                'headline': 'High Risk: Fabricated Claim',
                'detail': 'Contains statistical signatures of fake news, and zero corroborating journalistic reports were found.'
            }
