from dotenv import load_dotenv
import asyncio
import sys
import typing as t
import logging
from typing import AsyncIterator
import json

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq

from src.utils.mcp_servers import get_server_configs, MCPServers, get_all_tools
from src.utils.agent_config import AgentConfig, load_agent_config

load_dotenv()

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run(tools: list[BaseTool], prompt: str, agent_config: AgentConfig) -> str:
    """Run the agent with the given tools and prompt."""
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None) 
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    
    logger.debug(f"Available tools: {list(tools_map.keys())}")
    
    messages: list[BaseMessage] = [
        SystemMessage(content=agent_config.system_prompt),
        HumanMessage(content=prompt)
    ]
    
    while True:
        # Get response from model
        logger.debug("Sending request to model...")
        response = await tools_model.ainvoke(messages)
        logger.debug(f"Raw model response: {response}")
            
        # Convert response to AIMessage if it isn't already
        if not isinstance(response, AIMessage):
            ai_message = AIMessage(content=response)
        else:
            ai_message = response
            
        logger.debug(f"AI message content: {ai_message.content}")
        logger.debug(f"AI message tool calls: {ai_message.tool_calls}")
            
        messages.append(ai_message)
        
        # If no tool calls, we're done
        if not ai_message.tool_calls:
            logger.debug("No more tool calls, returning final response")
            return ai_message.content
        
        # Handle tool calls
        logger.debug(f"Tool calls requested: {len(ai_message.tool_calls)}")
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"].lower()
            if tool_name not in tools_map:
                logger.warning(f"Tool '{tool_name}' was requested but is not available")
                continue
                
            logger.debug(f"Executing tool: {tool_name}")
            selected_tool = tools_map[tool_name]
            
            # Add required fields for sequential-thinking server
            if tool_name == "sequentialthinking":
                args = json.loads(tool_call.args)
                logger.debug(f"Sequential thinking raw args: {args}")
                tool_call = {
                    "name": "sequentialthinking",
                    "arguments": {
                        "thought": args.get("thought", ""),
                        "thoughtNumber": args.get("thoughtNumber", 1),
                        "totalThoughts": args.get("totalThoughts", 5),
                        "isRevision": args.get("isRevision", False),
                        "revisesThought": args.get("revisesThought"),
                        "branchFromThought": args.get("branchFromThought"),
                        "branchId": args.get("branchId"),
                        "needsMoreThoughts": args.get("needsMoreThoughts", True),
                        "nextThoughtNeeded": args.get("nextThoughtNeeded", True)
                    }
                }
                logger.debug(f"Sequential thinking processed args: {tool_call['arguments']}")
            
            tool_msg = await selected_tool.ainvoke(tool_call)
            logger.debug(f"Tool response: {tool_msg.content}")
            messages.append(tool_msg)

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