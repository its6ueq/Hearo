import re
from collections import Counter

def extract_keywords_from_text(text: str, max_words: int = 15) -> list[str]:
    if not text or not text.strip():
        return []

    words = text.split()

    first_words = words[:max_words]
    
    print(f"AI Service: Got topic hint -> {first_words}")
    return first_words


def get_info_for_keyword(keyword: str) -> str:
    print(f"AI Service: Lấy thông tin cho '{keyword}'")
    test_html = f"""
        <h3>UI Test for Keyword: <span class="keyword">{keyword}</span></h3>
        <p>Lần 1: <strong>{keyword}</strong></p>
        <p>Lần 2: <strong>{keyword}</strong></p>
        <p>Lần 3: <strong>{keyword}</strong></p>
        <hr>
        <p><i>test HTML.</i></p>
        <p><i>Xem sếch ít thôi, hoa mắt rồi đó</i></p>
    """
        
    return test_html