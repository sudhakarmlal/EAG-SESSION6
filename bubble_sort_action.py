from typing import Dict, Any, Union, Tuple
from pydantic import BaseModel
from mcp import ClientSession
import ast
import datetime

def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

class ToolCallResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Union[str, list, dict]
    raw_response: Any

def parse_function_call(response: str) -> Tuple[str, Dict[str, Any]]:
    """Parses FUNCTION_CALL string into tool name and arguments."""
    try:
        if not response.startswith("FUNCTION_CALL:"):
            raise ValueError("Not a valid FUNCTION_CALL")

        _, function_info = response.split(":", 1)
        parts = [p.strip() for p in function_info.split("|")]
        func_name, param_parts = parts[0], parts[1:]

        arguments = {}
        for part in param_parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            try:
                arguments[key] = ast.literal_eval(value)
            except:
                arguments[key] = value.strip()

        log("parser", f"Parsed: {func_name} → {arguments}")
        return func_name, arguments

    except Exception as e:
        log("parser", f"Parse error: {e}")
        raise

async def execute_tool(session: ClientSession, tools: list, response: str) -> ToolCallResult:
    """Executes a sorting tool via MCP session."""
    try:
        tool_name, arguments = parse_function_call(response)
        
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        log("tool", f"Calling '{tool_name}' with: {arguments}")
        result = await session.call_tool(tool_name, arguments=arguments)
        
        if hasattr(result, 'content'):
            if isinstance(result.content, list) and result.content:
                output = result.content[0].text
            else:
                output = str(result.content)
        else:
            output = str(result)

        log("tool", f"Tool result: {output}")
        return ToolCallResult(
            tool_name=tool_name,
            arguments=arguments,
            result=output,
            raw_response=result
        )

    except Exception as e:
        log("tool", f"Tool execution error: {e}")
        raise

# Export the necessary functions
__all__ = ['execute_tool', 'ToolCallResult', 'parse_function_call']