from fastapi import APIRouter
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import graph
import traceback

router = APIRouter(prefix="/chat", tags=["chat"])


def _serialize_message(msg) -> dict:
    """Convert a LangChain BaseMessage to a JSON-serializable dict."""
    base = {
        "role": _role_from_type(msg),
        "content": msg.content if isinstance(msg.content, str) else str(msg.content),
    }
    # Include tool_calls if present (AIMessage with tool calls)
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        base["tool_calls"] = [
            {
                "id": tc.get("id", ""),
                "name": tc.get("name", ""),
                "args": tc.get("args", {}),
            }
            for tc in msg.tool_calls
        ]
    # Include tool metadata for ToolMessage
    if isinstance(msg, ToolMessage):
        base["tool_call_id"] = msg.tool_call_id
        base["name"] = getattr(msg, "name", None)
    return base


def _role_from_type(msg) -> str:
    if isinstance(msg, HumanMessage):
        return "user"
    if isinstance(msg, AIMessage):
        return "assistant"
    if isinstance(msg, ToolMessage):
        return "tool"
    if isinstance(msg, SystemMessage):
        return "system"
    return "assistant"


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        # Convert incoming messages to LangChain format
        lc_messages = []
        for msg in payload.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            # Skip tool/system messages from client — agent manages those

        initial_state = {
            "messages": lc_messages,
            "model": payload.model,
            "rep_id": payload.rep_id,
        }

        final_state = await graph.ainvoke(initial_state)

        # Serialize all messages (skip system message at index 0 added by agent)
        serialized = []
        for msg in final_state["messages"]:
            if isinstance(msg, SystemMessage):
                continue
            serialized.append(_serialize_message(msg))

        return ChatResponse(messages=serialized)

    except Exception as e:
        tb = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "Agent error",
                "detail": str(e),
                "messages": [
                    {
                        "role": "assistant",
                        "content": f"I encountered an error: {str(e)}. Please try again.",
                    }
                ],
            },
        )
