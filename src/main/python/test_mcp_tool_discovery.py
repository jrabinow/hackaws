#!/usr/bin/env python3
"""
Test script for MCP tool discovery.

This script initializes the MCP client, discovers available tools, and prints them.
It can be used to test and verify the tool discovery implementation.
"""

import logging
import sys
import time
from pprint import pprint

from duck.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)


def main():
    """Main function to test MCP tool discovery."""
    print("Starting MCP tool discovery test...")

    # Create an MCP client
    print("\nInitializing MCP client with auto_launch=True...")
    client = MCPClient(auto_launch=True)

    try:
        # Discover tools from all servers
        print("\nDiscovering tools from all servers...")
        tools = client.discover_tools()

        # Print discovered tools
        print(f"\nDiscovered {len(tools)} tools from MCP servers:")
        for i, tool in enumerate(tools, 1):
            print(f"\n--- Tool {i} ---")
            print(f"Server: {tool.get('server_name')}")
            print(f"Tool: {tool.get('tool_name')}")
            print(f"Description: {tool.get('description')}")
            print(f"Schema: {tool.get('schema')}")

        # Test force refresh
        print("\nTesting force refresh of tools cache...")
        tools = client.discover_tools(force_refresh=True)
        print(f"Rediscovered {len(tools)} tools after force refresh")

    except Exception as e:
        print(f"Error during tool discovery: {str(e)}")

    finally:
        # Clean up resources
        print("\nCleaning up resources...")
        client.cleanup()

    print("\nMCP tool discovery test completed.")


if __name__ == "__main__":
    main()
