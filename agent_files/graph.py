from langgraph.graph import END, START, StateGraph
 
from .agents import python_agent, web_research_agent, writer_agent
from .state import AgentState
 
 
def build_graph():
    graph = StateGraph(AgentState)
 
    graph.add_node("web_research_agent", web_research_agent)
    graph.add_node("python_agent", python_agent)
    graph.add_node("writer_agent", writer_agent)
 
    graph.add_edge(START, "web_research_agent")
    graph.add_edge("web_research_agent", "python_agent")
    graph.add_edge("python_agent", "writer_agent")
    graph.add_edge("writer_agent", END)
 
    return graph.compile()
 
 
app = build_graph()