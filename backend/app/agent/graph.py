from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from app.agent.state import AgentState
from app.agent.llm import get_llm
from app.agent.prompts import get_system_prompt
from app.tools import ALL_TOOLS


def agent_node(state: AgentState):
    """Main reasoning node — calls the LLM with all tools bound."""
    llm = get_llm(state.get("model", "llama-3.1-8b-instant"))
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    messages = list(state["messages"])

    # Prepend system message if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        system_msg = SystemMessage(content=get_system_prompt(state.get("rep_id", "rep_001")))
        messages = [system_msg] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def build_graph() -> StateGraph:
    tools_node = ToolNode(ALL_TOOLS)

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile()


# Singleton graph instance
graph = build_graph()
