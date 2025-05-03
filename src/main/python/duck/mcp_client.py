

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

    def __init__(self, auto_launch=False):
        """Initialize the MCP client.

        Args:
            auto_launch: If True, automatically launch servers defined with commands
            config_path: Path to the MCP configuration file (default from MCP_CONFIG_PATH env var or mcp.json)
        """
        self.config_path = os.getenv(
            "MCP_CONFIG_PATH",  os.path.join(os.getcwd(), "mcp.json"))
        self.config = self._load_config()
        self.clients = {}  # Dictionary of server_name -> Client
        self.server_processes = {}  # Dictionary of server_name -> Process
        self._initialize_clients(auto_launch)
        self.tools_cache = {}  # Cache for discovered tools

    def _initialize_clients(self, auto_launch=False):
        """Initialize clients for each MCP server in the configuration.

        Args:
            auto_launch: If True, automatically launch servers defined with commands
        """
        import subprocess
        import time

        for server_name, server_config in self.config.get("mcpServers", {}).items():
            try:
                # Extract server configuration
                server_url = server_config.get("url")
                command = server_config.get("command")
                args = server_config.get("args", [])

                # Launch the server if auto_launch is True and command is provided
                if auto_launch and command and not server_url:
                    try:
                        logger.info(f"Launching MCP server: {server_name}")
                        # Launch the server as a subprocess
                        cmd = [command] + args
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        self.server_processes[server_name] = process

                        # Wait a moment for the server to start
                        time.sleep(2)

                        # Determine the URL based on the server name
                        # Many MCP servers use a predictable port pattern
                        server_url = f"http://localhost:{8000 + hash(server_name) % 1000}"
                        logger.info(
                            f"Started server {server_name} at {server_url}")
                    except Exception as launch_error:
                        logger.error(
                            f"Error launching server {server_name}: {str(launch_error)}")

                # Create a client with the appropriate transport
                if server_url:
                    # Pass the URL as the transport parameter
                    logger.info(
                        f"Initializing client for {server_name} with URL: {server_url}")
                    self.clients[server_name] = Client(transport=server_url)
                elif command:
                    # If command is provided but no URL, try to derive a default URL
                    default_url = f"http://localhost:{8000 + hash(server_name) % 1000}"
                    logger.info(
                        f"Initializing client for {server_name} with default URL: {default_url}")
                    self.clients[server_name] = Client(transport=default_url)
                else:
                    logger.warning(
                        f"No URL or command found for server {server_name}, using default client")
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

    def refresh_tools_cache(self, server_name=None):
        """Refresh the tools cache for specified server or all servers.

        Args:
            server_name: Name of the server to refresh, or None to refresh all servers
        """
        if server_name:
            if server_name in self.tools_cache:
                del self.tools_cache[server_name]
                logger.info(f"Cleared tools cache for server: {server_name}")
        else:
            self.tools_cache = {}
            logger.info("Cleared all tools caches")

    def discover_tools(self, force_refresh=False) -> List[Dict[str, Any]]:
        """Discover available MCP tools by interrogating servers.

        Args:
            force_refresh: If True, ignore cached tools and rediscover all tools

        Returns:
            A list of tool definitions with server_name, tool_name, description, and schema
        """
        if force_refresh:
            self.refresh_tools_cache()

        tools = []

        try:
            # Iterate through all clients
            for server_name, client in self.clients.items():
                # Skip if we've already cached this server's tools
                if not force_refresh and server_name in self.tools_cache:
                    tools.extend(self.tools_cache[server_name])
                    continue

                try:
                    server_tools = []

                    # Get available tools from the server
                    server_info = client.get_server_info()

                    # Process server tools from the server info
                    if server_info and "tools" in server_info:
                        for tool in server_info["tools"]:
                            tool_info = {
                                "server_name": server_name,
                                "tool_name": tool.get("name"),
                                "description": tool.get("description", f"Tool for {server_name}"),
                                "schema": tool.get("input_schema", {})
                            }
                            server_tools.append(tool_info)
                    else:
                        # Fallback: Try to get tools using list_tools if available
                        try:
                            tools_list = client.list_tools()
                            for tool in tools_list:
                                tool_info = {
                                    "server_name": server_name,
                                    "tool_name": tool.get("name"),
                                    "description": tool.get("description", f"Tool for {server_name}"),
                                    "schema": tool.get("input_schema", {})
                                }
                                server_tools.append(tool_info)
                        except Exception as tool_error:
                            logger.warning(
                                f"Could not list tools from {server_name}: {str(tool_error)}")
                            # If both methods fail, add a placeholder tool but log a warning
                            logger.warning(
                                f"Adding placeholder tool for {server_name} - proper tool discovery failed")
                            server_tools.append({
                                "server_name": server_name,
                                "tool_name": f"{server_name}_default_tool",
                                "description": f"Default tool for {server_name} (proper discovery failed)",
                                "schema": {}
                            })

                    # Cache the tools for this server
                    self.tools_cache[server_name] = server_tools
                    tools.extend(server_tools)
                except Exception as e:
                    logger.error(
                        f"Error discovering tools for server {server_name}: {str(e)}")
                    # Add a placeholder tool to ensure functionality, but with an error note
                    error_tool = {
                        "server_name": server_name,
                        "tool_name": f"{server_name}_default_tool",
                        "description": f"Default tool for {server_name} (error during discovery: {str(e)})",
                        "schema": {}
                    }
                    tools.append(error_tool)

        except Exception as e:
            logger.error(f"Error discovering MCP tools: {str(e)}")

        return tools

    def cleanup(self):
        """Cleanup resources, terminating any server processes that were started.

        This method should be called when the application is shutting down to ensure
        proper termination of any server processes that were started by this client.
        """
        logger.info("Cleaning up MCP client resources")
        for server_name, process in list(self.server_processes.items()):
            try:
                logger.info(f"Terminating MCP server process: {server_name}")
                process.terminate()
                # Wait up to 5 seconds for graceful termination
                process.wait(timeout=5)
                logger.info(f"MCP server process terminated: {server_name}")
            except Exception as e:
                logger.warning(
                    f"Error terminating server process {server_name}: {str(e)}")
                try:
                    # Force kill if termination fails
                    process.kill()
                    logger.info(
                        f"MCP server process forcefully killed: {server_name}")
                except Exception as kill_error:
                    logger.error(
                        f"Failed to kill server process {server_name}: {str(kill_error)}")

            # Remove from processes dictionary
            self.server_processes.pop(server_name, None)

        # Clear other resources
        self.clients = {}
        self.tools_cache = {}
        logger.info("MCP client cleanup completed")

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
