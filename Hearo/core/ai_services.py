import re 
from collections import Counter
import spacy
from threading import Lock
from .keyword_extractor import KeywordExtractor
from .search_engine import get_info_for_keyword

import spacy_stanza, stanza
stanza.download('vi')

_PIPE_CACHE = {}

def make_nlp(lang: str = "en"):
    lang = (lang or "en").lower()
    if lang in _PIPE_CACHE:
        return _PIPE_CACHE[lang]

    if lang.startswith("en"):
        nlp = spacy.load("en_core_web_sm", exclude=["parser"])
        if "sentencizer" not in nlp.pipe_names and "senter" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
    elif lang.startswith("vi"):
        nlp = spacy_stanza.load_pipeline("vi")
    else:
        raise ValueError(f"Unsupported language: {lang}")

    _PIPE_CACHE[lang] = nlp
    return nlp

nlp = make_nlp("en")

ke = KeywordExtractor(
    nlp,
    use_noun_chunks=False,
    use_ner=True,
    use_lemma=True
)

_ke_lock = Lock()

def extract_keywords_from_text(
    text: str,
    *,
    mode: str = "new",
    top_k: int = 15,
    order: str = "appearance"
) -> list[str]:
    if not text or not text.strip():
        return []

    with _ke_lock:
        if mode == "new":
            new_keywords = ke.update(text, return_new_meta=False)
            if not new_keywords:
                return []
            print(f"AI Service: New keywords -> {new_keywords}")
            return new_keywords
        else:
            ke.update(text, return_new_meta=False)
            keywords = ke.get_top(top_k, order=order, return_meta=False)
            print(f"AI Service: Top keywords -> {keywords}")
            return keywords

def get_info_for_keyword_ui(keyword: str) -> str:
    print(f"AI Service: Lấy thông tin cho '{keyword}'")
    return get_info_for_keyword(keyword, lang="en")  