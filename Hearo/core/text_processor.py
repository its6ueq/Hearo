import re
from difflib import SequenceMatcher
from . import ai_services
from ..config.app_config import TextProcessorConfig

class EnhancedTextProcessor:
    def __init__(self, config: TextProcessorConfig = None):
        if config is None:
            config = TextProcessorConfig()
            
        self.similarity_threshold = config.similarity_threshold
        self.overlap_threshold = config.overlap_threshold
        self.max_buffer_size = config.max_buffer_size

        self.processed_sentences = []
        self.raw_buffer = []

    
    def similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_overlap(self, text1, text2):
        words1 = text1.lower().split()
        words2 = text2.lower().split()
        max_overlap, overlap_words = 0, 0
        for i in range(1, min(len(words1), len(words2)) + 1):
            if words1[-i:] == words2[:i]:
                overlap_words = i
        if overlap_words > 0:
            return overlap_words / min(len(words1), len(words2)), overlap_words
        return 0, 0
    
    def merge_overlapping_texts(self, text1, text2):
        overlap_ratio, overlap_words = self.find_overlap(text1, text2)
        if overlap_ratio >= self.overlap_threshold:
            merged_words = text1.split() + text2.split()[overlap_words:]
            return " ".join(merged_words), True
        return text1 + " " + text2, False
    
    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(um|uh|er|ah)\b', '', text, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', text).strip()
    
    def is_duplicate(self, new_text):
        new_text_clean = self.clean_text(new_text)
        if len(new_text_clean) < 10: return False
        
        check_buffer = self.processed_sentences[-10:]
        for existing in check_buffer:
            if self.similarity(new_text_clean, self.clean_text(existing)) >= self.similarity_threshold:
                return True
        return False
    
    def process_text(self, new_text):
        if not new_text or not new_text.strip():
            return "", False
        
        cleaned_text = self.clean_text(new_text)
        if not cleaned_text:
            return "", False

        if self.is_duplicate(cleaned_text):
            print(f"Duplicate detected: '{cleaned_text[:50]}...'")
            return "", False
        
        self.raw_buffer.append(cleaned_text)
        if len(self.raw_buffer) > self.max_buffer_size:
            self.raw_buffer.pop(0)

        if self.processed_sentences:
            last_sentence = self.processed_sentences[-1]
            merged, did_merge = self.merge_overlapping_texts(last_sentence, cleaned_text)
            if did_merge:
                print("Merged overlapping text")
                self.processed_sentences[-1] = merged
                return merged, True
        
        self.processed_sentences.append(cleaned_text)
        return cleaned_text, True

    def get_full_text(self):
        return " ".join(self.processed_sentences)

    def get_latest_sentences(self, count=2):
        return self.processed_sentences[-count:]

    def extract_keywords_from_text(self, text: str) -> list[str]:
        return ai_services.extract_keywords_from_text(text)

    def get_info_for_keyword(self, keyword: str) -> str:
        return ai_services.get_info_for_keyword(keyword)

    def clear(self):
        self.processed_sentences = []
        self.raw_buffer = []
        print("Enhanced text processor cleared")