from dotenv import load_dotenv
import asyncio
import sys
import typing as t
from typing import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq

from src.utils.mcp_servers import get_server_configs, MCPServers, get_all_tools
from src.utils.agent_config import AgentConfig, load_agent_config

load_dotenv()

async def run(tools: list[BaseTool], prompt: str, agent_config: AgentConfig) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None) 
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    messages: list[BaseMessage] = [
        SystemMessage(content=agent_config.system_prompt),
        HumanMessage(content=prompt)
    ]
    ai_message = t.cast(AIMessage, await tools_model.ainvoke(messages))
    messages.append(ai_message)
    
    # Handle tool calls if any
    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"].lower()
            if tool_name not in tools_map:
                print(f"Warning: Tool '{tool_name}' was requested but is not available. Skipping this tool call.")
                continue
            selected_tool = tools_map[tool_name]
            tool_msg = await selected_tool.ainvoke(tool_call)
            messages.append(tool_msg)
        
        # Get final response after tool usage
        final_response = await (tools_model | StrOutputParser()).ainvoke(messages)
        return final_response
    else:
        # If no tools were used, return the AI's direct response
        return ai_message.content


async def main(prompt: str) -> None:
    agent_config = load_agent_config()
    server_configs = get_server_configs()
    async with MCPServers(server_configs) as servers:
        all_tools = await get_all_tools(servers)
        response = await run(all_tools, prompt, agent_config)
        print(response)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./README.md"
    asyncio.run(main(prompt))