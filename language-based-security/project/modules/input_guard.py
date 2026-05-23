# optimistic filter
def words_matching_simple(prompt: str, malicious_phrases: list) -> int:
    # first layer of guarding
    """This is the first guardrail, only tries to match a naive way, explicitly drop
    any visible malicious intention

    Keyword arguments:
    prompt (string) -- raw input from user
    Return: 0 if danger, otherwise 1
    """
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