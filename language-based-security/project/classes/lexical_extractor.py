import re

class LexicalExtractor:
    """
    Locally extractor to separate user's intentions and data inputs (if any).
    """
    def __init__(self):
        """
        Constructor
        """
        # match with the Markdown block
        self.markdown_pattern = re.compile(r"(.*?)(```.+?```)(.*)", re.DOTALL)

        # match with common keywords that users usually use
        self.keyword_pattern = re.compile(
            r"(.*?)(?:\n|\s)(Error:|Code:|Traceback:|Context:|Logs:)(.*)", 
            re.IGNORECASE | re.DOTALL
        )
        
        self.logger_indicate = 1

    def extract(self, raw_prompt: str) -> dict:
        """Extract method, to separate the user's intentions, instructions with data
        
        Keyword arguments:
        raw_prompt -- user's prompt, unstructural, mixed with data
        Return: A dictionary contains {"user's intention": "", "user's data": ""}
        """

        markdown_match = self.markdown_pattern.search(raw_prompt)
        keyword_match = self.keyword_pattern.search(raw_prompt)


        if markdown_match:
            if self.logger_indicate == 1:
                print(f"[LOG] Found matched results: {markdown_match}")
            # treat all the data outside of the backticks is intent, then data
            # since code in markdown is indicated by backticks
            intention = (markdown_match.group(1) + " " + markdown_match.group(3)).strip()
            data = markdown_match.group(2).strip()
            return {"intentions": intention, "data": data}
        elif keyword_match:
            if self.logger_indicate == 1:
                print(f"[LOG] Found matched results: {keyword_match}")
            intention = (keyword_match.group(1) + " " + keyword_match.group(2)).strip()
            data = (keyword_match.group(3)).strip()
            return {"intentions": intention, "data": data}
        else:
            if self.logger_indicate == 1:
                print("[LOG] No structural boundaries found. Defaulting to pure intent.")
            return {"intentions": raw_prompt.strip(), "data": None}
