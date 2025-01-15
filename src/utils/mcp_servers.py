import pathlib
import json
import os
import logging
import shutil
import subprocess
from dataclasses import dataclass
from contextlib import AsyncExitStack
from typing import AsyncIterator

from langchain_core.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp import MCPToolkit

# Configure module logger
logger = logging.getLogger("server")

@dataclass
class ServerConfig:
    """Configuration for an MCP server."""
    name: str
    server_params: StdioServerParameters

def get_server_configs() -> list[ServerConfig]:
    """Get the list of server configurations filtered by mcpServers in config.json."""
    # Read allowed servers from config.json
    try:
        with open("config.json") as f:
            config = json.load(f)
        allowed_servers = set(config.get("mcpServers", []))
        logger.debug(f"Allowed servers from config: {allowed_servers}")
    except FileNotFoundError:
        logger.error("config.json not found")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config.json")
        raise

    # Get paths to node and npx
    npm_prefix = subprocess.run(['npm', 'config', 'get', 'prefix'], 
                              capture_output=True, 
                              text=True).stdout.strip()
    node_path = shutil.which('node')
    npx_path = os.path.join(npm_prefix, 'bin', 'npx')
    
    logger.debug(f"Using node at: {node_path}")
    logger.debug(f"Using npx at: {npx_path}")
    
    # Ensure the environment has the correct PATH
    env = os.environ.copy()
    env['PATH'] = f"{os.path.dirname(node_path)}:{env.get('PATH', '')}"
    
    # Define available servers
    all_servers = [
        ServerConfig(
            name="filesystem",
            server_params=StdioServerParameters(
                command=npx_path,
                args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent.parent)],
                env=env
            )
        ),
        ServerConfig(
            name="memory",
            server_params=StdioServerParameters(
                command=npx_path,
                args=["-y", "@modelcontextprotocol/server-memory"],
                env=env
            )
        ),
        ServerConfig(
            name="brave-search",
            server_params=StdioServerParameters(
                command=npx_path,
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={**env, "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY")}
            )
        ),
        ServerConfig(
            name="sequential-thinking",
            server_params=StdioServerParameters(
                command=npx_path,
                args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
                env=env
            )
        ),
        ServerConfig(
            name="github",
            server_params=StdioServerParameters(
                command="docker",
                args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "mcp/github"],
                env={**env, "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")}
            )
        )
    ]

    # Filter servers based on config
    filtered_servers = [server for server in all_servers if server.name in allowed_servers]
    logger.debug(f"Filtered server configurations: {[s.name for s in filtered_servers]}")
    return filtered_servers

class MCPServers:
    """Context manager for handling multiple MCP servers."""
    
    def __init__(self, configs: list[ServerConfig]):
        self.configs = configs
        self.exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        
    async def __aenter__(self) -> "MCPServers":
        for config in self.configs:
            try:
                logger.info(f"Starting server: {config.name}")
                read, write = await self.exit_stack.enter_async_context(
                    stdio_client(config.server_params)
                )
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                self.sessions[config.name] = session
                logger.debug(f"Successfully started server: {config.name}")
            except Exception as e:
                logger.error(f"Failed to start server {config.name}: {str(e)}")
                await self.exit_stack.aclose()
                raise
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        logger.debug("Closing all server sessions...")
        await self.exit_stack.aclose()
        logger.debug("Successfully closed all server sessions")
    
    def get_session(self, name: str) -> ClientSession:
        """Get a session by name."""
        return self.sessions[name]

async def get_all_tools(servers: MCPServers) -> list[BaseTool]:
    """Initialize and get tools from all servers."""
    tools_logger = logging.getLogger("tools")
    all_tools = []
    
    for name, session in servers.sessions.items():
        tools_logger.debug(f"Initializing tools for server: {name}")
        toolkit = MCPToolkit(session=session)
        await toolkit.initialize()
        tools = toolkit.get_tools()
        all_tools.extend(tools)
        tools_logger.debug(f"Added {len(tools)} tools from server: {name}")
    
    return all_tools 