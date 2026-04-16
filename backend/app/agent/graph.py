import json
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, ToolMessage
from app.agent.state import AgentState
from app.agent.llm import get_llm
from app.agent.prompts import get_system_prompt
from app.tools import ALL_TOOLS


def _sanitize_messages(messages: list) -> list:
    """Ensure every ToolMessage has non-empty string content.

    Groq rejects tool messages whose content is an empty string or empty list.
    Convert any non-string / empty content to a JSON string so the API accepts it.
    """
    sanitized = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            content = msg.content
            # Convert list/dict content to a JSON string
            if not isinstance(content, str):
                content = json.dumps(content) if content is not None else "(no result)"
            # Guard against empty string
            if not content or not content.strip():
                content = "(no result)"
            msg = ToolMessage(
                content=content,
                tool_call_id=msg.tool_call_id,
                name=getattr(msg, "name", None),
            )
        sanitized.append(msg)
    return sanitized


async def agent_node(state: AgentState):
    """Main reasoning node — calls the LLM with all tools bound."""
    llm = get_llm(state.get("model", "llama-3.1-8b-instant"))
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    messages = list(state["messages"])

    # Prepend system message if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        system_msg = SystemMessage(content=get_system_prompt(state.get("rep_id", "rep_001")))
        messages = [system_msg] + messages

    # Sanitize ToolMessage content before sending to Groq
    messages = _sanitize_messages(messages)

    response = await llm_with_tools.ainvoke(messages)
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
