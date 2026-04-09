from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
 
from config import llm
from state import AgentState
from tools import extract_url, run_python, search_web
 
 
# ============================================================
# Generic helper for tool-calling agents
# ============================================================
def run_agent_with_tools(
    system_prompt: str,
    user_prompt: str,
    tools: list,
    max_loops: int = 4,
) -> str:
    tool_map = {t.name: t for t in tools}
    model = llm.bind_tools(tools)
 
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
 
    for _ in range(max_loops):
        ai_msg = model.invoke(messages)
        messages.append(ai_msg)
 
        if not ai_msg.tool_calls:
            return str(ai_msg.content)
 
        for tool_call in ai_msg.tool_calls:
            result = tool_map[tool_call["name"]].invoke(tool_call["args"])
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )
 
    return "Stopped after reaching the tool-call limit."
 
 
# ============================================================
# Agent 1: Web research specialist
# ============================================================
def web_research_agent(state: AgentState) -> AgentState:
    prompt = f"""
User task:
{state["user_task"]}
 
Your job:
- You are ONLY the web research specialist.
- If fresh web info is useful, use search_web and optionally extract_url.
- Prefer 2-3 strong sources, not a flood of links.
- Return a compact research note.
- If web lookup is not needed, return exactly: WEB_NOT_NEEDED
""".strip()
 
    output = run_agent_with_tools(
        system_prompt=(
            "You are WebResearchAgent. Do not solve the whole task. "
            "Only gather web findings relevant to the request."
        ),
        user_prompt=prompt,
        tools=[search_web, extract_url],
    )
    return {"web_notes": output}
 
 
# ============================================================
# Agent 2: Python execution specialist
# ============================================================
def python_agent(state: AgentState) -> AgentState:
    prompt = f"""
User task:
{state["user_task"]}
 
Web findings:
{state.get("web_notes", "WEB_NOT_NEEDED")}
 
Your job:
- You are ONLY the Python execution specialist.
- Use run_python only if calculation, parsing, transformation, or a tiny script would help.
- Return a compact execution note.
- If Python execution is not needed, return exactly: PYTHON_NOT_NEEDED
""".strip()
 
    output = run_agent_with_tools(
        system_prompt=(
            "You are PythonAgent. Do not provide the final user answer. "
            "Only decide whether Python should be run, and run it if useful."
        ),
        user_prompt=prompt,
        tools=[run_python],
    )
    return {"python_notes": output}
 
 
# ============================================================
# Agent 3: Final writer specialist
# ============================================================
def writer_agent(state: AgentState) -> AgentState:
    messages = [
        SystemMessage(
            content=(
                "You are WriterAgent. Your only job is to create the final answer "
                "for the user using the specialist outputs below. "
                "Ignore WEB_NOT_NEEDED and PYTHON_NOT_NEEDED if present."
            )
        ),
        HumanMessage(
            content=f"""
Original task:
{state["user_task"]}
 
WebResearchAgent output:
{state.get("web_notes", "")}
 
PythonAgent output:
{state.get("python_notes", "")}
 
Write the final answer clearly and concisely.
""".strip()
        ),
    ]
 
    final = llm.invoke(messages).content
    return {"final_answer": str(final)}
 