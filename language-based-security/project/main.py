import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

sys.path.append(project_root)

import json, html, socket

from modules.input_guard import words_matching_simple
from modules.regex_matching import RegexFilter
from modules.vector_matching import *

from classes.lexical_extractor import LexicalExtractor

SOCKET_PATH = "/tmp/prompt_protection.sock"

class PromptProtectionDaemon:
    def __init__(self):
        print("[INIT] Booting daemon (Python 3.13)...")
        self.regex_filter = RegexFilter()
        self.extractor = LexicalExtractor()

        self.DROP_SCORE = 0.85
        self.QUARANTINE_SCORE = 0.70

    def escape_and_tag(self, data_frame: str) -> str:
        """Apply DataSec XML isolation to the data portion"""
        if not data_frame:
            return ""
        escaped_data = html.escape(data_frame, quote=True)
        return f"\n<user_context>\n{escaped_data}\n<user_context>"

    def process_pipeline(self, raw_prompt: str) -> str:
        """Apply multi-stages sanitized methods for user's input"""

        if words_matching_simple(raw_prompt) == 0:
            return{"status": "BLOCKED",
                    "reason": "Naive string match."
                    }

        if not self.regex_filter.scan(raw_prompt):
            return {"status": "BLOCKED",
                    "reason": "Matching attacking patterns."
                    }
        query_vector = vectorized_sentence(raw_prompt, word_index, vocabulary)
        similar_sentences = vector_db.find_similar_vectors(query_vector, num_results=2)
        highest_similarity = similar_sentences[0][1] if similar_sentences else 0.0