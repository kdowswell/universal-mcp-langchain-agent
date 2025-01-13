from dotenv import load_dotenv
import asyncio
import sys
import typing as t
import logging
from typing import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq

from src.utils.mcp_servers import get_server_configs, MCPServers, get_all_tools
from src.utils.agent_config import AgentConfig, load_agent_config

load_dotenv()

# Configure module logger
logger = logging.getLogger("agent")

async def run(tools: list[BaseTool], prompt: str, agent_config: AgentConfig) -> str:
    """Run the agent with the given tools and prompt."""
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None) 
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    
    if agent_config.logging.verbose:
        logger.debug(f"Available tools: {list(tools_map.keys())}")
    
    messages: list[BaseMessage] = [
        SystemMessage(content=agent_config.system_prompt),
        HumanMessage(content=prompt)
    ]
    
    # Get initial response from model
    logger.debug("Sending initial request to model...")
    ai_message = t.cast(AIMessage, await tools_model.ainvoke(messages))
    if agent_config.logging.verbose:
        logger.debug(f"Initial AI response: {ai_message.content}")
    messages.append(ai_message)
    
    # Handle tool calls if any
    if ai_message.tool_calls:
        logger.debug(f"Tool calls requested: {len(ai_message.tool_calls)}")
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"].lower()
            if tool_name not in tools_map:
                logger.warning(f"Tool '{tool_name}' was requested but is not available")
                continue
                
            logger.debug(f"Executing tool: {tool_name}")
            selected_tool = tools_map[tool_name]
            tool_msg = await selected_tool.ainvoke(tool_call)
            if agent_config.logging.verbose:
                logger.debug(f"Tool response: {tool_msg.content}")
            messages.append(tool_msg)
        
        # Get final response after tool usage
        logger.debug("Getting final response from model...")
        final_response = await (tools_model | StrOutputParser()).ainvoke(messages)
        if agent_config.logging.verbose:
            logger.debug(f"Final response: {final_response}")
        return final_response
    
    # If no tools were used, return the AI's direct response
    logger.debug("No tools were used, returning direct response")
    return ai_message.content

async def main(prompt: str) -> None:
    """Main entry point for the application."""
    try:
        agent_config = load_agent_config()
        server_configs = get_server_configs()
        
        async with MCPServers(server_configs) as servers:
            all_tools = await get_all_tools(servers)
            response = await run(all_tools, prompt, agent_config)
            
            print("\nAgent Response:")
            print("--------------")
            print(response)
            print("--------------")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Get prompt from command line or use default
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./README.md"
    
    # Run the application
    asyncio.run(main(prompt))