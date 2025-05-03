

import logging
import os
import traceback
from typing import Any, Callable, Dict, List, Optional

# Import LangChain components with updated package structure
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.format_scratchpad import format_to_tool_messages
from langchain.agents.output_parsers.openai_tools import \
    OpenAIToolsAgentOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Import the new MCP client
from duck.mcp_client import MCPClient


class LLMProvider:
    """Manages LLM provider integration based on environment configuration."""

    def __init__(self):
        """Initialize the LLM provider based on environment variables."""
        self.provider = os.getenv("MODEL_PROVIDER", "openai").lower()
        self.model = self._initialize_model()
        self.mcp_client = MCPClient()
        self.agent = self._initialize_agent()

    def _initialize_model(self):
        """Initialize the appropriate LLM model based on the provider."""
        if self.provider == "openai":
            return ChatOpenAI(
                model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model_name=os.getenv("ANTHROPIC_MODEL", "claude-2"),
                temperature=0.7,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            # Default to OpenAI if provider not recognized
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )

    def _initialize_agent(self):
        """Initialize a LangChain agent with dynamically discovered MCP tools."""
        # Create tools for each MCP tool
        tools = []

        # Discover available MCP tools
        mcp_tools = self.mcp_client.discover_tools()

        # Create a LangChain tool for each MCP tool
        for mcp_tool in mcp_tools:
            server_name = mcp_tool["server_name"]
            tool_name = mcp_tool["tool_name"]
            description = mcp_tool["description"]

            # Create a function that calls the MCP tool
            def create_tool_func(server=server_name, tool=tool_name):
                def tool_func(*args, **kwargs):
                    # Handle positional arguments if provided
                    if args:
                        # Convert the first positional argument to a parameter the tool expects
                        return self.mcp_client.use_tool(server, tool, {"input": args[0]})
                    return self.mcp_client.use_tool(server, tool, kwargs)
                return tool_func

            # Create a LangChain tool
            tools.append(
                Tool(
                    name=f"{server_name}_{tool_name}",
                    func=create_tool_func(server_name, tool_name),
                    description=description
                )
            )

        # Create a proper prompt template for the agent
        system_message = "You are a helpful assistant for debuggging tasks."
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create the agent with the prompt template
        agent = create_openai_tools_agent(
            self.model,
            tools,
            prompt
        )

        # Create the agent executor with a specific output key
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=False,
            output_key="output"  # Specify an output key to fix the run() issue
        )

    def chat(self,
             query: str,
             system_prompt: Optional[str] = None,
             chat_history: Optional[List[Dict[str, str]]] = None,
             use_agent: bool = False) -> str:
        """Generate a response using the configured LLM.

        Args:
            query: The user's query
            system_prompt: Optional system prompt to guide the model
            chat_history: Optional chat history for context
            use_agent: Whether to use the agent with tools

        Returns:
            The model's response as a string
        """
        if use_agent:
            # Use the agent with tools
            try:
                # Use invoke instead of run
                result = self.agent.invoke({"input": query})
                return result.get("output", "I couldn't generate a response using tools.")
            except Exception as e:
                logging.error(traceback.format_exc())
                logging.error(f"Agent execution failed: {str(e)}")
                return f"I encountered an error while trying to use tools: {str(e)}. Let me try to answer without tools."
        else:
            # Use the model directly
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))

            # Add chat history if provided
            if chat_history:
                for message in chat_history:
                    if message["role"] == "user":
                        messages.append(HumanMessage(
                            content=message["content"]))
                    elif message["role"] == "assistant":
                        messages.append(AIMessage(content=message["content"]))

            # Add the current query
            messages.append(HumanMessage(content=query))

            # Get response from the model
            response = self.model.invoke(messages)

            return response.content
