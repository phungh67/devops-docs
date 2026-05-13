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
import modules.sandboxing as sandbox

SOCKET_PATH = "/tmp/llm_guard_client.sock"

class LLGuardDaemon:
    """
    Class definition for the LLM (Prompt Injection) Guard Daemon
    """
    def __init__(self):
        self.extractor = LexicalExtractor()
        self.regex_filter = RegexFilter()

        # configuration toggle
        self.embedding_mode = False
        self.is_execution = False

        # premade database, limited cases
        self.vocabulary = construct_vocabulary(sentences)
        self.word_index = construct_word_indexes(self.vocabulary)
        sentence_vectors = vectorized_input_database(sentences, self.word_index, self.vocabulary)

        # construct vector database
        self.vector_db = VectorDatabase()
        for sentence, vector in sentence_vectors.items():
            self.vector_db.add_vector(sentence, vector)

        # output modular
        self.sanitinzed_prompt = {}

        # store the pending (safe) actions
        self.pending_execution_steps = []

        # reinforcement for the matching database
        self.embedding_vector_db = VectorDatabase()

        self.ollama_connector = OllamaConnector()

        self.verbose_log = 0

        self.DROP_SCORE = 0.63
        self.QUARANTINE_SCORE = 0.45

    def toggle_log(self):
        """Helper method to enable log"""
        self.verbose_log = 1

    def toggle_sandbox_execution(self):
        """Helper method to enable sandboxing execution"""
        self.is_execution = True

    def update_inner_vector_database(self, sentence: str):
        sentences.append(sentence)
        self.vocabulary = construct_vocabulary(sentences)
        self.word_index = construct_word_indexes(self.vocabulary)
        sentence_vectors = vectorized_input_database(sentences, self.word_index, self.vocabulary)

        self.vector_db.clear()
        for sentence, vector in sentence_vectors.items():
            self.vector_db.add_vector(sentence, vector)

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

        threat_detected = False
        threat_flags = []

        # indicate the execution status

        if words_matching_simple(raw_input) == 0:
            threat_detected = True
            threat_flags.append("Stage 1: Known malicious phrase(s).")

        if not self.regex_filter.scan(raw_input):
            threat_detected = True
            threat_flags.append("Stage 2: Obfuscation/Base64.")


        query_vector = vectorized_sentence(raw_input, self.word_index, self.vocabulary)
        similar_sentences = self.vector_db.find_similar_vectors(query_vector, num_results=2)
        highest_similarity = similar_sentences[0][1] if similar_sentences else 0.0

        # print(f"[INFO] Vector similarity detection Score: {highest_similarity:.4f}")

        if highest_similarity >= self.DROP_SCORE:
            threat_detected = True
            threat_flags.append(f"Stage 3: Semantic match with {highest_similarity:.2f}")
        elif highest_similarity >= self.QUARANTINE_SCORE:
            if self.verbose_log:
                print("[WARN] Payload quarantined. Applying stricter LLM guardrails...")

            embedding_vector = self.ollama_connector.generate_embedded_vector(raw_input)

            if isinstance(embedding_vector, list):
                self.embedding_vector_db.add_vector(raw_input, embedding_vector)
                if self.verbose_log:
                    print("[LOG] Threat embedding successfully stored in dense database.")
            else:
                if self.verbose_log:
                    print("[ERROR] Failed to generate embedding. Bypassing dense storage.")
        
        if self.embedding_mode == True:

            embedding_query_vector = self.ollama_connector.generate_embedded_vector(raw_input)
            if isinstance(embedding_query_vector, list):
                similar_sentences_embedding = self.embedding_vector_db.find_similar_vectors(query_vector=embedding_query_vector, num_results=2)
                highest_similarity_embedding = similar_sentences_embedding[0][1] if similar_sentences_embedding else 0.0

                if highest_similarity >= self.DROP_SCORE:
                    threat_detected = True
                    threat_flags.append(f"Stage 4 (Optional): Semantic match with {highest_similarity_embedding:.2f}")
            else:
                if self.verbose_log:
                    print("[ERROR] Failed to generate embedding for active defense check.")

        extracted = self.extractor.extract(raw_input)
        intent = extracted.get("intentions", "")
        data = extracted.get("data", None)

        safe_xml_data = self.frame_data(intent, data)

        self.sanitinzed_prompt = {
            "status": "SANITIZED" if threat_detected else "APPROVED",
            "threat_flags": threat_flags,
            "safe_payload": safe_xml_data
        }

        return self.sanitinzed_prompt
    
    def sandbox_execution(self, llm_response: str) -> str:
        """
        Method to execute step by step with pre generated response from earlier stages
        Keyword arguments:
        llm_response -- string representation of the response
        Return -- unknow yet
        """

        # native parser
        steps = sandbox.parse_steps(llm_response)

        final_output = ""

        # if not null
        if steps:
            playground = sandbox.Sandbox()
            playground.start()

            exec_results = sandbox.execute_steps(steps, mode='all', sandbox=playground)
            changed_files = playground.changed_files()

            playground.stop()

            final_output = "**HAL Execution Plan:**\n```text\n"
            final_output += "\n".join(exec_results)
            if changed_files:
                final_output += f"\n\n[SANDBOX] {len(changed_files)} files modified in memory."
            final_output += "\n```"
                                
        return final_output
    
    def handler_prompt_result(self, prompt_result: dict) -> dict:
        """
        Helper function for DRY
        """
        if prompt_result["status"] in ["APPROVED", "SANITIZED"]:
            if self.verbose_log:
                print("[REQUEST OUT] Payload is sanitized and ready for Ollama.")
                llm_data = self.ollama_connector.generate_chat(prompt_result["safe_payload"])
                if "error" in llm_data:
                    prompt_result = {"status": "ERROR", "reason": llm_data["error"]}
                else:
                    # bugs: neutralized prompt did not generate a response
                    llm_response = llm_data.get("message", {}).get("content", "")
                    if not llm_response.strip():
                        # check the status, if blank because of guard
                        if prompt_result["status"] == "SANITIZED":
                            llm_response = "> The system detected a malcious payload in previous prompt, all threats were neutralized, I'm ready for the next command. *"
                        else:
                            llm_response = "Hello, what's a nice day, how can I help you?"

                    prompt_result["llm_response"] = llm_response
                    self.sanitinzed_prompt["last_llm_response"] = prompt_result["llm_response"]
                    
                    # only delete (to free "space") if the result was safe
                    if "safe_payload" in prompt_result:
                        del prompt_result["safe_payload"]
        return prompt_result
                

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

                # handle /commit command (apply changes to plan)
                if raw_data.strip().lower() == "/commit":
                    if self.pending_execution_steps:
                        # check if there is any steps in the state machine?
                        if self.verbose_log:
                            print("[DAEMON] Escalating execution to the real system...")

                        real_results = sandbox.execute_steps(self.pending_execution_steps, mode='all', sandbox=None)
                        self.pending_execution_steps = [] # upon succesfully executed, clean it

                        report = "**Real System Update:**\n```text\n" + "\n".join(real_results) + "\n```"
                        conn.sendall(json.dumps({"status": "EXECUTED", "llm_response": report}).encode('utf-8'))

                # handle discard command (got plan but chose to not go with it)
                if raw_data.strip().lower() == "/discard":
                    self.pending_execution_steps = []
                    conn.sendall(json.dumps({"status": "EXECUTED", "llm_response": "Execution plan discarded. Ready for next command."}).encode('utf-8'))
                    conn.close()
                    continue
                # handle execution command
                if raw_data.strip().lower().startswith("/execution") and self.is_execution == True:
                    raw_data = raw_data.strip()[10:].strip()

                    # check if the data only contain /execute tag
                    if not raw_data:
                        # branching logic here: if currently sanitized and stored
                        if self.sanitinzed_prompt and "last_llm_response" in self.sanitinzed_prompt:
                            llm_response_str = self.sanitinzed_prompt.get("last_llm_response")
                            execution_result = self.sandbox_execution(llm_response_str)
                            conn.sendall(json.dumps({"status": "EXECUTED", "llm_response": execution_result}).encode('utf-8'))
                        else:
                            conn.sendall(json.dumps({"status": "ERROR", "llm_response": "No previous chat history to execute."}).encode('utf-8'))
                        conn.close()
                        continue
                    # else /execution command went with data
                    else:
                        processed_dict = self.process_input(raw_data)

                        # appended the system prompt to this dictionary
                        processed_dict["safe_payload"] += f"\n\n{sandbox.SYSTEM_PROMPT}"

                        execution_prompt = self.handler_prompt_result(processed_dict)

                        llm_response_str = execution_prompt.get("llm_response", "")
                        execution_result = self.sandbox_execution(llm_response_str)

                        conn.sendall(json.dumps({"status": "EXECUTED", "llm_response": execution_result}).encode('utf-8'))
                        conn.close()
                        continue

                result = self.process_input(raw_data)

                self.handler_prompt_result(result)

                conn.sendall(json.dumps(result).encode('utf-8'))
                conn.close()
        except KeyboardInterrupt:
            print("\n[DAEMON] Shutting down...")
        finally:
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)   

if __name__ == "__main__":
    daemon = LLGuardDaemon()
    daemon.start()        