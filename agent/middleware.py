from langchain.agents.middleware import (
    AgentState,
    ModelRequest,
    Runtime,
    before_model,
    dynamic_prompt,
    wrap_tool_call,
)
from utils.logger_handler import logger
from utils.prompt_loader import load_main_prompt, load_report_prompt
from langgraph.prebuilt.tool_node import ToolCallRequest
from typing import Callable
from langchain_core.messages import ToolMessage
from langgraph.types import Command


def _has_called_fill_context_for_report(messages) -> bool:
    """Return True if the agent has already called fill_context_for_report."""
    for msg in messages:
        tool_calls = getattr(msg, "tool_calls", None) or []
        for tc in tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            if name == "fill_context_for_report":
                return True
    return False


# 1) Runs BEFORE each model call
@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> None:
    messages = state.get("messages", [])
    in_report_mode = _has_called_fill_context_for_report(messages)
    logger.info(
        f"[before_model] message_count={len(messages)}, report_mode={in_report_mode}"
    )
    return None


# 2) Runs when building the model request: choose system prompt
@dynamic_prompt
def report_prompt_switch(request: ModelRequest) -> str:
    messages = request.state.get("messages", [])
    if _has_called_fill_context_for_report(messages):
        logger.info("[dynamic_prompt] using report_prompt")
        return load_report_prompt()
    logger.info("[dynamic_prompt] using main_prompt")
    return load_main_prompt()


# 3) Supervisor: wraps every tool execution (logging + error handling)
@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    tool_call = getattr(request, "tool_call", None)
 
    if isinstance(tool_call, dict):
        tool_name = tool_call.get("name", "unknown_tool")
        tool_args = tool_call.get("args", {})
    else:
        tool_name = getattr(tool_call, "name", "unknown_tool")
        tool_args = getattr(tool_call, "args", {})
 
    logger.info(f"[wrap_tool_call] start tool={tool_name}, args={tool_args}")
 
    try:
        result = handler(request)
        logger.info(f"[wrap_tool_call] done tool={tool_name}")
        return result
    except Exception as e:
        logger.error(
            f"[wrap_tool_call] tool={tool_name} failed: {e}", exc_info=True
        )
        raise
