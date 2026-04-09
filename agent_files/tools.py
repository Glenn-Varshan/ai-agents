import json
import os
import subprocess
import sys
import tempfile
 
from ddgs import DDGS
from langchain_core.tools import tool
 
 
@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web and return a compact JSON list of results."""
    results = DDGS().text(query, max_results=max_results)
    cleaned = [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in results[:max_results]
    ]
    return json.dumps(cleaned, ensure_ascii=False, indent=2)
 
 
@tool
def extract_url(url: str) -> str:
    """Fetch and extract page content as markdown-like text."""
    data = DDGS().extract(url, fmt="text_markdown")
    content = data.get("content", "")
    return content[:6000]
 
 
@tool
def run_python(code: str) -> str:
    """
    Run short local Python code with a timeout.
    Demo only: do NOT expose this directly to untrusted users.
    """
    FORBIDDEN_PATTERNS = [
        "import os",
        "import subprocess",
        "import socket",
        "import shutil",
        "from os",
        "from subprocess",
        "__import__",
        "open(",
    ]
 
    if any(pattern in code.lower() for pattern in FORBIDDEN_PATTERNS):
        return "Rejected: unsafe code pattern detected."
 
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        path = f.name
 
    try:
        proc = subprocess.run(
            [sys.executable, "-I", path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        parts = []
        if proc.stdout.strip():
            parts.append("STDOUT:\n" + proc.stdout.strip())
        if proc.stderr.strip():
            parts.append("STDERR:\n" + proc.stderr.strip())
        return "\n\n".join(parts) if parts else "No output."
    except subprocess.TimeoutExpired:
        return "Execution timed out after 10 seconds."
    finally:
        try:
            os.remove(path)
        except OSError:
            pass