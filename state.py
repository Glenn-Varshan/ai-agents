from typing_extensions import TypedDict


# ============================================================
# Shared state
# ============================================================
class AgentState(TypedDict, total=False):
    user_task: str
    web_notes: str
    python_notes: str
    final_answer: str
 