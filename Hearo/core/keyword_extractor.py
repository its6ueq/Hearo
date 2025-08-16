# keyword_extractor.py
from __future__ import annotations
from collections import Counter
from typing import Dict, List, Iterable, Optional, Tuple
import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

NER_LABELS_PRIORITY = {
    "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "FAC"
}

def _build_np_matcher(nlp):
    """Xây 1 lần: cụm (ADJ)* (NOUN|PROPN)+ hoặc (NOUN|PROPN)+"""
    m = Matcher(nlp.vocab)
    p1 = [{"POS": "ADJ", "OP": "*"}, {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}]
    p2 = [{"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}]
    m.add("NOUN_PHRASE", [p1, p2])
    return m

def _contiguous_propn_spans(doc):
    spans, start = [], None
    for i, tok in enumerate(doc):
        if tok.pos_ == "PROPN" and not tok.is_stop and tok.is_alpha:
            if start is None:
                start = i
        else:
            if start is not None:
                spans.append(doc[start:i])
                start = None
    if start is not None:
        spans.append(doc[start:len(doc)])
    return spans

def _clean_edges(span):
    """Cắt bớt từ rìa ít thông tin: DET/ADP/CCONJ/SCONJ/PART/PRON + stopwords."""
    start, end = span.start, span.end
    bad = {"DET", "ADP", "CCONJ", "SCONJ", "PART", "PRON"}
    doc = span.doc
    while start < end and (doc[start].is_stop or doc[start].pos_ in bad):
        start += 1
    while end > start and (doc[end-1].is_stop or doc[end-1].pos_ in bad):
        end -= 1
    return doc[start:end]

def _sent_index_map(doc):
    sid = {}
    try:
        for si, s in enumerate(doc.sents):
            for t in s:
                sid[t.i] = si
        if not sid:
            for t in doc: sid[t.i] = 0
    except Exception:
        for t in doc: sid[t.i] = 0
    return sid

class KeywordExtractor:
    """
    Trình trích xuất tối ưu cho streaming:
      - update(text|Doc) liên tục
      - get_top(...) để lấy bảng xếp hạng hiện tại
      - trả keyword mới sinh ở mỗi lần update
    """
    def __init__(
        self,
        nlp,
        *,
        min_char: int = 2,
        use_noun_chunks: bool = True,
        use_ner: bool = True,
        weight_ner: float = 1.5,
        weight_propn: float = 1.2,
        use_lemma: bool = True
    ):
        self.nlp = nlp
        self.min_char = min_char
        self.use_noun_chunks = use_noun_chunks
        self.use_ner = use_ner
        self.weight_ner = weight_ner
        self.weight_propn = weight_propn
        self.use_lemma = use_lemma

        # Trạng thái tích lũy
        self.global_freq = Counter()     
        self.seen = set()                
        self.meta: Dict[str, dict] = {}  
        self._tok_offset = 0          
        self._sent_offset = 0

        # Tài nguyên dựng 1 lần
        self.matcher = _build_np_matcher(nlp)

        # Cache token hóa cụm để tính điểm nhanh
        self._phrase_token_cache: Dict[str, List[str]] = {}

    def _token_key(self, tok):
        return (tok.lemma_ if self.use_lemma and tok.lemma_ else tok.text).lower()

    def _normalize_phrase(self, text: str) -> str:
        return text.strip().lower()

    def _phrase_tokens(self, phrase: str) -> List[str]:
        k = phrase.lower()
        if k in self._phrase_token_cache:
            return self._phrase_token_cache[k]
        dt = self.nlp.make_doc(phrase)
        toks = [t.text.lower() for t in dt if not t.is_punct and not t.is_space]
        self._phrase_token_cache[k] = toks
        return toks

    def _collect_candidates(self, doc) -> List:
        sent_id_map = _sent_index_map(doc)
        spans = []

        # (A) NER (ưu tiên)
        if self.use_ner and hasattr(doc, "ents"):
            for ent in doc.ents:
                if ent.label_ in NER_LABELS_PRIORITY:
                    sp = _clean_edges(ent)
                    if len(sp):
                        spans.append(("ner", sp))

        # (B) PROPN chuỗi
        for sp in _contiguous_propn_spans(doc):
            sp = _clean_edges(sp)
            if len(sp): spans.append(("propn", sp))

        # (C) Cụm danh từ
        if self.use_noun_chunks and doc.has_annotation("DEP") and hasattr(doc, "noun_chunks"):
            for ch in doc.noun_chunks:
                sp = _clean_edges(ch)
                if len(sp): spans.append(("chunk", sp))
        else:
            matches = self.matcher(doc)
            raw = filter_spans([doc[s:e] for _, s, e in matches])
            for sp in raw:
                sp = _clean_edges(sp)
                if len(sp): spans.append(("match", sp))

        # Lọc theo độ dài & trùng lặp vị trí
        seen_span = set()
        out = []
        for typ, sp in spans:
            t = sp.text.strip()
            if len(t) < self.min_char: 
                continue
            sig = (sp.start, sp.end)
            if sig in seen_span:
                continue
            seen_span.add(sig)
            out.append((typ, sp, sent_id_map.get(sp.start, 0)))
        return out

    def _update_freq(self, doc):
        self.global_freq.update(self._token_key(w) for w in doc if not w.is_punct and not w.is_space)

    def update(self, text_or_doc, *, return_new_meta: bool = True):
        """Xử lý 1 batch text/Doc, trả về danh sách keyword mới (theo thời gian)."""
        doc = text_or_doc if hasattr(text_or_doc, "to_array") else self.nlp(text_or_doc)

        self._update_freq(doc)

        candidates = self._collect_candidates(doc)
        new_items = []

        for typ, sp, sent_local in candidates:
            phrase = sp.text.strip()
            key = self._normalize_phrase(phrase)
            if not key: 
                continue

            # vị trí toàn cục
            tok_i_global = self._tok_offset + sp.start
            sent_id_global = self._sent_offset + sent_local

            if key not in self.meta:
                has_propn = any(t.pos_ == "PROPN" for t in sp)
                has_ner = (typ == "ner")
                self.meta[key] = {
                    "text": phrase,
                    "tok_i": tok_i_global,
                    "start_char": sp.start_char,
                    "sent_id": sent_id_global,
                    "has_propn": has_propn,
                    "has_ner": has_ner,
                }
                self.seen.add(key)
                new_items.append(self.meta[key])
            else:
                pass

        # tăng offset cho batch sau
        self._tok_offset += len(doc)
        try:
            last_sid = max(_sent_index_map(doc).values()) if len(doc) else -1
        except Exception:
            last_sid = -1
        self._sent_offset += (last_sid + 1)

        # trả keyword mới theo thứ tự xuất hiện
        if return_new_meta:
            return sorted(new_items, key=lambda m: m["tok_i"])
        else:
            return [m["text"] for m in sorted(new_items, key=lambda m: m["tok_i"])]

    def _score(self, phrase_text: str, meta: dict) -> float:
        toks = self._phrase_tokens(phrase_text)
        base = sum(self.global_freq.get(t, 0) for t in toks)
        # ưu tiên theo thuộc tính
        if meta.get("has_propn"): 
            base *= self.weight_propn
        if meta.get("has_ner"): 
            base *= self.weight_ner
        # nhẹ tay thưởng số token để ưu tiên cụm dài hơn một chút
        return base + 0.1 * len(toks)

    def get_top(self, top_k: int = 20, *, order: str = "score", return_meta: bool = False):
        items = list(self.meta.values())
        if order == "appearance":
            items.sort(key=lambda m: m["tok_i"])
        else:
            items.sort(key=lambda m: self._score(m["text"], m), reverse=True)
        out = items[:top_k]
        if return_meta:
            return [
                {**m, "score": float(self._score(m["text"], m))}
                for m in out
            ]
        return [m["text"] for m in out]

    def reset(self):
        self.global_freq.clear()
        self.seen.clear()
        self.meta.clear()
        self._tok_offset = 0
        self._sent_offset = 0
        self._phrase_token_cache.clear()

def extract_keywords(nlp, text, top_k=20, min_char=2, order="score", return_meta=False):
    ke = KeywordExtractor(nlp, min_char=min_char)
    ke.update(text)
    return ke.get_top(top_k, order=order, return_meta=return_meta)