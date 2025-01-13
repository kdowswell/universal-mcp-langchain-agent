import pathlib
import json
import os
from dataclasses import dataclass
from contextlib import AsyncExitStack
from typing import AsyncIterator

from langchain_core.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp import MCPToolkit


@dataclass
class ServerConfig:
    """Configuration for an MCP server."""
    name: str
    server_params: StdioServerParameters


def get_server_configs() -> list[ServerConfig]:
    """Get the list of server configurations filtered by mcpServers in config.json."""
    # Read allowed servers from config.json
    with open("config.json") as f:
        config = json.load(f)
    allowed_servers = set(config.get("mcpServers", []))

    # Define all available servers
    all_servers = [
        ServerConfig(
            name="filesystem",
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent.parent)],
            )
        ),
        ServerConfig(
            name="memory",
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-memory"],            
            )
        ),
    ]

    # Filter servers based on config
    return [server for server in all_servers if server.name in allowed_servers]


class MCPServers:
    """Context manager for handling multiple MCP servers."""
    
    def __init__(self, configs: list[ServerConfig]):
        self.configs = configs
        self.exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        
    async def __aenter__(self) -> "MCPServers":
        for config in self.configs:
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(config.server_params)
            )
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            self.sessions[config.name] = session
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.exit_stack.aclose()
    
    def get_session(self, name: str) -> ClientSession:
        """Get a session by name."""
        return self.sessions[name]


async def get_all_tools(servers: MCPServers) -> list[BaseTool]:
    """Initialize and get tools from all servers."""
    all_tools = []
    
    for name, session in servers.sessions.items():
        toolkit = MCPToolkit(session=session)
        await toolkit.initialize()
        all_tools.extend(toolkit.get_tools())
    
    return all_tools 