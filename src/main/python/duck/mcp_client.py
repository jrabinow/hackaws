

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import Client

# Set up logging
logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with MCP servers and tools."""

    def __init__(self):
        """Initialize the MCP client.

        Args:
            config_path: Path to the MCP configuration file (default: mcp.json)
        """
        self.config_path = os.getenv(
            "MCP_CONFIG_PATH",  os.path.join(os.getcwd(), "mcp.json"))
        self.config = self._load_config()
        self.clients = {}  # Dictionary of server_name -> Client
        self._initialize_clients()
        self.tools_cache = {}  # Cache for discovered tools

    def _initialize_clients(self):
        """Initialize clients for each MCP server in the configuration."""
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            try:
                # Create a client with the appropriate transport based on the server configuration
                server_url = server_config.get("url")
                if server_url:
                    # Pass the URL as the transport parameter
                    self.clients[server_name] = Client(transport=server_url)
                else:
                    logger.warning(
                        f"No URL found for server {server_name}, using default client")
                    # Create a default client with a default URL as transport
                    self.clients[server_name] = Client(
                        transport="http://localhost:3000")
            except Exception as e:
                logger.error(
                    f"Error initializing client for server {server_name}: {str(e)}")

    def _load_config(self) -> Dict[str, Any]:
        """Load the MCP configuration from the config file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                logger.warning(
                    f"MCP config file not found: {self.config_path}")
                return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"Error loading MCP config: {str(e)}")
            return {"mcpServers": {}}

    def use_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use an MCP tool.

        Args:
            server_name: The name of the MCP server
            tool_name: The name of the tool to use
            arguments: The arguments to pass to the tool

        Returns:
            The response from the tool, or None if an error occurred
        """
        logger.info(
            f"MCP tool call: {server_name}.{tool_name}({json.dumps(arguments)})")

        try:
            # Get the client for the specified server
            client = self.clients.get(server_name)
            if client is None:
                logger.error(f"No client found for server {server_name}")
                return None

            return client.use_tool(server_name, tool_name, arguments)
        except Exception as e:
            logger.error(f"Error using MCP tool: {str(e)}")
            return None

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available MCP tools by interrogating servers.

        Returns:
            A list of tool definitions with server_name, tool_name, description, and schema
        """
        tools = []

        try:
            # Iterate through all clients
            for server_name, client in self.clients.items():
                # Skip if we've already cached this server's tools
                if server_name in self.tools_cache:
                    tools.extend(self.tools_cache[server_name])
                    continue

                try:
                    # Since get_server_info is not available, we'll create a minimal
                    # set of tool information based on the server name
                    server_tools = []

                    # Add a placeholder tool for each server
                    # This is a temporary solution until we can properly discover tools
                    server_tools.append({
                        "server_name": server_name,
                        "tool_name": f"{server_name}_default_tool",
                        "description": f"Default tool for {server_name}",
                        "schema": {}
                    })

                    # Cache the tools for this server
                    self.tools_cache[server_name] = server_tools
                    tools.extend(server_tools)
                except Exception as e:
                    logger.error(
                        f"Error discovering tools for server {server_name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error discovering MCP tools: {str(e)}")

        return tools


# For backward compatibility
def use_mcp_tool(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Backward compatibility function for the original use_mcp_tool.

    Args:
        server_name: The name of the MCP server
        tool_name: The name of the tool to use
        arguments: The arguments to pass to the tool

    Returns:
        The response from the tool, or None if an error occurred
    """
    client = MCPClient()
    return client.use_tool(server_name, tool_name, arguments)
