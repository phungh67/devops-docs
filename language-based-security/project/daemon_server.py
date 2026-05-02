import socket
import os
import json
import html

from classes.lexical_extractor import LexicalExtractor
from classes.regex_filter import RegexFilter
from classes.vector_db import VectorDatabase
from classes.ollama_connector import OllamaConnector

from modules.input_guard import words_matching_simple
from modules.vector_matching import (
    construct_vocabulary,
    construct_word_indexes,
    vectorized_input_database,
    vectorized_sentence,
    sentences
)

SOCKET_PATH = "/tmp/prompt_injection_guard.sock"

class PromptInjectionGuardDaemon:
    """
    Class definition for the Prompt Injection Guard Daemon
    """
    def __init__(self):
        self.extractor = LexicalExtractor()
        self.regex_filter = RegexFilter()

        self.vocabulary = construct_vocabulary(sentences)
        self.word_index = construct_word_indexes(self.vocabulary)
        sentence_vectors = vectorized_input_database(sentences, self.word_index, self.vocabulary)

        self.vector_db = VectorDatabase()
        for sentence, vector in sentence_vectors.items():
            self.vector_db.add_vector(sentence, vector)

        self.ollama_connector = OllamaConnector()

        self.verbose_log = 0

        self.DROP_SCORE = 0.80
        self.QUARANTINE_SCORE = 0.45

    def toggle_log(self):
        """Helper method to enable log"""
        self.verbose_log = 1
    

    def frame_data(self, intent: str, data: str) -> str:
        """Santitizes and wraps text extracted in XML tags."""
        safe_intent = html.escape(intent.strip(), quote=True)
        final_payload = f"<user_input>\n{safe_intent}\n</user_input>"

        if data:
            data = data.strip()
            
            if data.startswith("```") and data.endswith("```"):
                lines = data.split('\n')
                if len(lines) >= 2:
                    data = '\n'.join(lines[1:-1]).strip()

            safe_data = html.escape(data, quote=True)
            final_payload += f"\n<data>\n{safe_data}\n</data>"

        return final_payload

    def process_input(self, raw_input: str) -> dict:
        """Detect, extract and sanitize user's input"""

        if words_matching_simple(raw_input) == 0:
            return {"status": "BLOCKED", "reason": "Failed Stage 1: Naive string match."}

        if not self.regex_filter.scan(raw_input):
            return {"status": "BLOCKED", "reason": "Failed Stage 2: Obfuscation/Structural match."}

        query_vector = vectorized_sentence(raw_input, self.word_index, self.vocabulary)
        similar_sentences = self.vector_db.find_similar_vectors(query_vector, num_results=2)
        highest_similarity = similar_sentences[0][1] if similar_sentences else 0.0

        print(f"[INFO] Vector similarity detection Score: {highest_similarity:.4f}")

        if highest_similarity >= self.DROP_SCORE:
            return {"status": "BLOCKED", "reason": "Failed Stage 3: Semantic similarity to known attacks."}


        extracted = self.extractor.extract(raw_input)
        intent = extracted.get("intentions", "")
        data = extracted.get("data", None)

        safe_xml_data = self.frame_data(intent, data)

        return {
            "status": "APPROVED",
            "safe_payload": safe_xml_data
        }

    def start(self):
        """Start method of the class"""

        # remove existing socker if existed
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        # bind daemon to a UNIX socket
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(5)

        if self.verbose_log:
            print(f"\n[DAEMON] Module 1 active. Listening on {SOCKET_PATH}...")

        try:
            while True:
                # accept payload
                conn, addr = server.accept()
                raw_data = conn.recv(8192).decode('utf-8')

                # else continue to listening new "packets"
                if not raw_data:
                    conn.close()
                    continue
                
                if self.verbose_log:
                    print("-" * 60)
                    print(f"[REQUEST IN] {raw_data[:50]}...")

                result = self.process_input(raw_data)

                conn.sendall(json.dumps(result).encode('utf-8'))
                conn.close()

                if result["status"] == "APPROVED":
                    print("[REQUEST OUT] Payload is sanitized and ready for Ollama.")
        except KeyboardInterrupt:
            print("\n[DAEMON] Shutting down...")
        finally:
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)   

if __name__ == "__main__":
    daemon = PromptInjectionGuardDaemon()
    daemon.start()        