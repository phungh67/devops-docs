# first layer of guarding

# global
malicious_phrases = [
    "ignore previous",
    "disregard previous",
    "forget all instructions",
    "system prompt",
    "developer mode",
    "you are now",
    "print your instructions",
    "bypass filters",
    "do not filter",
]

# optimistic filter
def words_matching_simple(prompt: str):
    print("[LOG]Checking if in the prompt contained malicious phrases...")

    # strip spaces and lower all the words
    sanitized_prompt = " ".join(prompt.lower().split())

    for phrase in malicious_phrases:
        if phrase in sanitized_prompt:
            print(f"[DANGER] The prompt contains malicious phrase '{phrase}',this incident will be notified to administrator")
            return 0
    return 1

if __name__ == "__main__":
    demo_prompt = "There is a bug, I need to    bypass        filters to check the bug"
    indicate = words_matching_simple(demo_prompt)
    print(f"[INFO] The previous prompt was handled with return code of: {indicate}")