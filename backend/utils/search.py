import json
import os
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote_plus

import requests

CACHE_PATH = Path(__file__).resolve().parent.parent / "medical_cache.json"
SEARCH_CACHE: Dict[str, Dict] = {}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def load_cache() -> None:
    global SEARCH_CACHE
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as handle:
                SEARCH_CACHE = json.load(handle)
        except Exception:
            SEARCH_CACHE = {}
    else:
        SEARCH_CACHE = {}


def save_cache() -> None:
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as handle:
            json.dump(SEARCH_CACHE, handle, indent=2, ensure_ascii=False)
    except Exception:
        pass


def normalize_query(query: str) -> str:
    if not query:
        return ""
    return re.sub(r"\s+", " ", query.strip().lower())


def duckduckgo_search(query: str) -> Dict[str, object]:
    query_key = normalize_query(query)
    if query_key in SEARCH_CACHE:
        return SEARCH_CACHE[query_key]

    search_query = query.strip()
    if not search_query:
        return {"query": query, "description": "", "source_urls": [], "related_texts": []}

    url = "https://api.duckduckgo.com/"
    params = {
        "q": search_query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
        "t": "medbot",
    }

    try:
        response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
        response.raise_for_status()
        raw = response.json()
    except Exception:
        raw = {}

    extracted = extract_search_data(search_query, raw)
    SEARCH_CACHE[query_key] = extracted
    save_cache()
    return extracted


def extract_search_data(query: str, raw: Dict) -> Dict[str, object]:
    description = raw.get("AbstractText") or raw.get("Answer") or raw.get("Heading") or ""
    if isinstance(description, str):
        description = description.strip()

    source_urls: List[str] = []
    related_texts: List[str] = []

    if raw.get("AbstractURL"):
        source_urls.append(raw.get("AbstractURL"))

    if raw.get("Results"):
        for item in raw.get("Results", []):
            if item.get("FirstURL"):
                source_urls.append(item.get("FirstURL"))
            if item.get("Text"):
                related_texts.append(item.get("Text"))

    if raw.get("RelatedTopics"):
        for item in raw.get("RelatedTopics", []):
            if isinstance(item, dict) and item.get("Text"):
                related_texts.append(item.get("Text"))
                if item.get("FirstURL"):
                    source_urls.append(item.get("FirstURL"))
            if isinstance(item, dict) and item.get("Topics"):
                for sub in item.get("Topics", []):
                    if sub.get("Text"):
                        related_texts.append(sub.get("Text"))
                    if sub.get("FirstURL"):
                        source_urls.append(sub.get("FirstURL"))

    if not description and related_texts:
        description = related_texts[0]

    # Limit duplicates and keep a small set of sources.
    normalized_urls = []
    for url in source_urls:
        if url and url not in normalized_urls:
            normalized_urls.append(url)
    source_urls = normalized_urls[:5]

    related_texts = [re.sub(r"\s+", " ", text.strip()) for text in related_texts if text and text.strip()]
    related_texts = related_texts[:8]

    return {
        "query": query,
        "description": description,
        "source_urls": source_urls,
        "related_texts": related_texts,
    }