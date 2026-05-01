import html

def frame_data(raw_data: str) -> str:
    """Sanitize a raw data, separate with XML tag, use html to escape special characters"""
    if not data:
        return ""
    
    data = data.strip()
    if data.startswith("```") and data.endswith("```"):
        lines = data.split('\n')
        if len(lines) >= 2: 
            data = '\n'.join(lines[1:-1]).strip()
    
    escaped_data = html.escape(data, quote=True)
    