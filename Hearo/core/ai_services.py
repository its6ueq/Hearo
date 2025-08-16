import re 
from collections import Counter
import spacy
from threading import Lock
from .keyword_extractor import KeywordExtractor

# --- Load spaCy 1 lần, tối ưu tốc độ ---
# Tắt parser (không cần noun_chunks), giữ NER + lemmatizer
nlp = spacy.load("en_core_web_sm", exclude=["parser"])
# Sentencizer để có doc.sents khi parser bị tắt
if "sentencizer" not in nlp.pipe_names and "senter" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

# Khởi tạo extractor (tối ưu cho streaming)
ke = KeywordExtractor(
    nlp,
    use_noun_chunks=False,   # nhanh hơn (dùng POS-matcher)
    use_ner=True,            # ưu tiên thực thể (PERSON/ORG/GPE...)
    use_lemma=True           # đếm tần suất theo lemma -> chính xác hơn
)

# Nếu multi-thread/callback song song, dùng lock để tránh race-condition
_ke_lock = Lock()

def extract_keywords_from_text(
    text: str,
    *,
    mode: str = "new",        # "new": trả keyword mới | "top": bảng top hiện tại
    top_k: int = 15,
    order: str = "appearance" # "appearance" hoặc "score"
) -> list[str]:
    """
    - mode="new": trả về các keyword MỚI phát sinh từ 'text' (theo thứ tự xuất hiện)
    - mode="top": cập nhật trạng thái rồi trả về top_k keyword hiện có
    """
    if not text or not text.strip():
        return []

    with _ke_lock:
        if mode == "new":
            # keyword mới của batch này (đã theo thứ tự thời gian)
            new_keywords = ke.update(text, return_new_meta=False)
            if not new_keywords:
                return []
            print(f"AI Service: New keywords -> {new_keywords}")
            return new_keywords
        else:
            # vẫn update trạng thái rồi lấy bảng top hiện tại
            ke.update(text, return_new_meta=False)
            keywords = ke.get_top(top_k, order=order, return_meta=False)
            print(f"AI Service: Top keywords -> {keywords}")
            return keywords

def get_info_for_keyword(keyword: str) -> str:
    print(f"AI Service: Lấy thông tin cho '{keyword}'")