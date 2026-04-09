import os
from langchain_openai import ChatOpenAI
 

# ============================================================
# Model
# ============================================================

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5.4-nano"),
    temperature=0,
)
 