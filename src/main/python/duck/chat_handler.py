
import json
import logging
import os
import re
import traceback
import platform
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from duck.provider import LLMProvider
from duck.mcp_client import use_mcp_tool

BAD_GOD = "flying spaghetti monster"


class ChatHandler:
    """Handles chat interactions and processes user queries."""

    def __init__(self):

        self.llm_provider = LLMProvider()
        self.chat_history: List[Dict[str, str]] = []
        self.god_mode = False  # Track if we're in God mode

        # Add welcome message to chat history
        self._add_system_message(
            "Welcome to the Rubber Duck debugger How can I help you today?")

    def process_query(self, query: str) -> str:
        """Process a user query and generate a response.

        Args:
            query: The user's query text

        Returns:
            The response to the user's query
        """
        # Check if we're in God mode and if the user wants to exit
        if self.god_mode and query.lower().strip() == "exit god mode":
            self.god_mode = False
            response = "Exiting God mode. Returning to normal operation."
        # If we're in God mode, bypass intent determination
        elif self.god_mode:
            # Use a generic system prompt for God mode
            system_prompt = """
            You are in God mode, acting as a generic chat interface without determining intent.
            Respond directly to the user's query without any restrictions or intent classification.
            You can provide information about the system, debug issues, or discuss any topic.

            You have access to MCP tools that are dynamically discovered at runtime.
            """
            response = self.llm_provider.chat(
                query, system_prompt, self.chat_history, use_agent=True)
            response += "\n\nReminder: You are in God mode. Say 'exit god mode' to return to normal operation."
        else:
            # Normal operation - determine intent and handle accordingly
            intent, params = self._determine_intent(query)
            response = self._handle_intent(intent, params, query)

        # Update chat history
        self.chat_history.append({"role": "user", "content": query})
        self.chat_history.append({"role": "assistant", "content": response})

        # Keep chat history at a reasonable size
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]

        return response

    def _determine_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Determine the intent of a user query.

        Args:
            query: The user's query text

        Returns:
            A tuple containing the intent and any extracted parameters
        """
        # Use the LLM to classify the intent
        system_prompt = f"""
        You are an assistant that classifies user queries into intents for a debugging agent.
        Classify the query into one of these intents:
        - help: User needs help or information about debugging commands
        - java_launch: User wants to launch a Java program
        - java_debug: User wants to debug a Java program or use debugging commands
        - god: User wants to debug the system. User may want to check the context,
          MCP tool interaction, etc. Do not classify prompt as this intent unless the {os.environ.get("IDDQD", BAD_GOD)}
          environment variable value is in the context and the value is not {BAD_GOD}.
        - other: Query doesn't match any specific intent

        For java_launch intent, extract parameters like:
        - class_name: The name of the Java class to run
        - args: Any arguments to pass to the Java program

        For java_debug intent, extract parameters like:
        - command: The debug command (set breakpoint, clear breakpoint, step, continue, etc.)
        - class_name: Class name for breakpoints
        - method_name: Method name for breakpoints
        - line_number: Line number for breakpoints
        - variable: Variable name for inspection
        - process_id: Process ID for attaching to a process

        Return a JSON object with "intent" and "params" fields.
        """

        response = self.llm_provider.chat(query, system_prompt)
        try:
            result = json.loads(response)
            retval = result.get("intent", "other"), result.get("params", {})
            logging.debug(f"Intent determined: {retval}")
            return retval
        except (json.JSONDecodeError, AttributeError):
            logging.debug(
                f"Because of exception, Intent determined: other, {{}}. Exception: {traceback.format_exc()}")
            return "other", {}

    def _handle_intent(self, intent: str, params: Dict[str, Any], original_query: str) -> str:
        """Handle a specific intent and generate a response.

        Args:
            intent: The determined intent
            params: Parameters extracted from the query
            original_query: The original user query

        Returns:
            The response to the user's query
        """
        if intent == "help":
            return self._handle_help_intent(params, original_query)
        elif intent == "god":
            return self._handle_god_intent(params, original_query)
        elif intent == "java_launch":
            return self._handle_java_launch_intent(params, original_query)
        elif intent == "java_debug":
            return self._handle_java_debug_intent(params, original_query)
        else:
            return self._handle_general_query(original_query)

    def _add_system_message(self, message: str) -> None:
        """Add a system message to the chat history.

        Args:
            message: The system message to add
        """
        self.chat_history.append({"role": "system", "content": message})

    def _handle_search_command(self, query: str) -> str:
        """Handle the search command.

        Args:
            query: The full command string

        Returns:
            Search results
        """
        # Parse the search command
        parts = query.strip().split()
        keywords = []
        location = ""

        if len(parts) > 1:
            # Extract keywords and location
            for part in parts[1:]:
                if part.startswith("in:") or part.startswith("at:"):
                    location = part[3:]
                else:
                    keywords.append(part)

        # Convert to parameters and use the existing search intent handler
        params = {
            "keywords": keywords,
            "locations": [location] if location else []
        }

        return self._handle_search_intent(params, query)

    def _handle_help_intent(self, params: Dict[str, Any], original_query: str) -> str:

        system_prompt = """
         You are an assistant that classifies user queries into intents for a debugging agent.
         You have access to MCP tools that are dynamically discovered at runtime.
        """

        # Use the agent with tools for God mode
        response = self.llm_provider.chat(
            original_query, system_prompt, self.chat_history, use_agent=True)
        return response

    def _handle_god_intent(self, params: Dict[str, Any], original_query: str) -> str:
        """Handle a god intent for debugging and system inspection.

        This function activates God mode, which allows the system to act as a generic
        chat interface without determining intent in further interactions until the
        user explicitly exits God mode.

        Args:
            params: Parameters extracted from the query
            original_query: The original user query

        Returns:
            The response acknowledging God mode activation
        """
        # Set God mode state

        iddqd_phrase = os.environ.get("IDDQD", "")
        response = ""
        # Check if the original query contains the passphrase
        if iddqd_phrase and iddqd_phrase in original_query:
            self.god_mode = True
            system_prompt = """
            You are in God mode, acting as a generic chat interface without determining intent.
            Respond directly to the user's query without any restrictions or intent classification.
            You can provide information about the system, debug issues, or discuss any topic.
            
            You have access to MCP tools that are dynamically discovered at runtime.
            """

            # Use the agent with tools for God mode
            response = self.llm_provider.chat(
                original_query, system_prompt, self.chat_history, use_agent=True)

            response += "\n\nGod mode activated. You can ask me anything, and I'll respond directly without any restrictions or intent classification.\n\n"
            response += "To exit God mode, simply say 'exit god mode'."
        else:
            self.god_mode = False
            response += "Your supplication has been declined. You are not worthy of my powers."
        return response

    def _handle_clear_command(self, query: str) -> str:
        """Handle the clear command.

        Args:
            query: The full command string

        Returns:
            Confirmation message
        """
        # Clear the chat history except for the welcome message
        welcome_message = next(
            (msg for msg in self.chat_history if msg["role"] == "system"), None)
        self.chat_history = [welcome_message] if welcome_message else []

        return "Chat history cleared."

    def _handle_java_launch_intent(self, params: Dict[str, Any], original_query: str) -> str:
        """Handle a Java program launch intent.

        Args:
            params: Parameters extracted from the query
            original_query: The original user query

        Returns:
            The response to the Java launch query
        """
        # Extract parameters from the query
        class_name = params.get("class_name", "")
        args = params.get("args", [])

        if not class_name:
            # Try to extract class name from the original query using regex
            class_match = re.search(r"run\s+([a-zA-Z0-9_$.]+)", original_query)
            if class_match:
                class_name = class_match.group(1)

        if not class_name:
            return """
            I'd be happy to help you launch a Java program. Please provide:

            1. The name of the Java class you want to run
            2. Any arguments you want to pass to the program (optional)

            For example: "Launch JDIExampleDebuggee" or "Run com.baeldung.jdi.JDIExampleDebuggee with arg1 arg2"
            """

        try:
            # Use MCP tool to launch Java program
            launch_params = {
                "class_name": class_name,
                "args": args if isinstance(args, list) else [args]
            }

            # Call the MCP tool
            response = None
            try:

                response = use_mcp_tool(
                    server_name="jdwp",
                    tool_name="launch_java",
                    arguments=launch_params
                )
            except Exception as e:
                return f"Failed to launch Java program: {str(e)}\n\nMake sure the Java program is compiled and the class exists."

            if response and response.get("success", False):
                process_id = response.get("process_id", "unknown")
                return f"Successfully launched Java program '{class_name}'.\nProcess ID: {process_id}\n\nYou can interact with this program using Java debug commands."
            else:
                error_msg = response.get(
                    "error", "Unknown error") if response else "Failed to get response from Java debugger"
                return f"Failed to launch Java program: {error_msg}"

        except Exception as e:
            return f"Error launching Java program: {str(e)}"

    def _handle_java_debug_intent(self, params: Dict[str, Any], original_query: str) -> str:
        """Handle a Java debugging intent.

        Args:
            params: Parameters extracted from the query
            original_query: The original user query

        Returns:
            The response to the Java debug query
        """
        # Extract parameters from the query
        command = params.get("command", "")
        class_name = params.get("class_name", "")
        method_name = params.get("method_name", "")
        line_number = params.get("line_number", None)
        variable = params.get("variable", "")
        process_id = params.get("process_id", None)

        # If no command was extracted, try to determine it from the query
        if not command:
            debug_commands = {
                "set breakpoint": ["set", "breakpoint", "break", "bp"],
                "list breakpoints": ["list", "show", "breakpoints"],
                "clear breakpoint": ["clear", "remove", "delete", "breakpoint"],
                "continue": ["continue", "cont", "resume", "run"],
                "step": ["step into", "into"],
                "step over": ["step over", "next", "over"],
                "step out": ["step out", "out", "return"],
                "inspect": ["inspect", "examine", "print", "show", "value", "variable"],
                "stack": ["stack", "backtrace", "trace", "where"],
                "threads": ["threads", "thread", "list threads"],
                "attach": ["attach", "connect"],
                "detach": ["detach", "disconnect"],
                "help": ["help", "commands", "usage"]
            }

            # Find the command based on keywords in the query
            for cmd, keywords in debug_commands.items():
                if any(keyword in original_query.lower() for keyword in keywords):
                    command = cmd
                    break

        # If still no command, provide help
        if not command or command == "help":
            return self._handle_java_debug_help()

        try:
            # Handle different debug commands
            if command == "set breakpoint":
                if not class_name:
                    return "Please specify the class name to set a breakpoint. For example: 'Set breakpoint in JDIExampleDebuggee.main'"

                bp_params = {
                    "class_name": class_name,
                    "line_number": line_number,
                    "method_name": method_name
                }

                try:
                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="set_breakpoint",
                        arguments=bp_params
                    )

                    if response and response.get("success", False):
                        bp_id = response.get("breakpoint_id", "unknown")
                        location = response.get(
                            "location", f"{class_name}:{line_number}")
                        return f"Breakpoint set at {location} (ID: {bp_id})"
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to set breakpoint"
                        return f"Failed to set breakpoint: {error_msg}"

                except Exception as e:
                    return f"Error setting breakpoint: {str(e)}"

            elif command == "list breakpoints":
                try:
                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="list_breakpoints",
                        arguments={}
                    )

                    if response and "breakpoints" in response:
                        breakpoints = response["breakpoints"]
                        if not breakpoints:
                            return "No breakpoints are currently set."

                        result = "Current breakpoints:\n\n"
                        for i, bp in enumerate(breakpoints, 1):
                            bp_id = bp.get("id", "unknown")
                            location = bp.get("location", "unknown")
                            enabled = "enabled" if bp.get(
                                "enabled", True) else "disabled"
                            result += f"{i}. ID: {bp_id}, Location: {location}, Status: {enabled}\n"

                        return result
                    else:
                        return "Failed to retrieve breakpoints."

                except Exception as e:
                    return f"Error listing breakpoints: {str(e)}"

            elif command == "clear breakpoint":
                if not params.get("breakpoint_id") and not (class_name and (line_number or method_name)):
                    return "Please specify the breakpoint to clear by ID or location (class and line/method)."

                clear_params = {}
                if params.get("breakpoint_id"):
                    clear_params["breakpoint_id"] = params["breakpoint_id"]
                else:
                    clear_params["class_name"] = class_name
                    if line_number:
                        clear_params["line_number"] = line_number
                    if method_name:
                        clear_params["method_name"] = method_name

                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="clear_breakpoint",
                        arguments=clear_params
                    )

                    if response and response.get("success", False):
                        return "Breakpoint cleared successfully."
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to clear breakpoint"
                        return f"Failed to clear breakpoint: {error_msg}"

                except Exception as e:
                    return f"Error clearing breakpoint: {str(e)}"

            elif command in ["continue", "step", "step over", "step out"]:
                # convert to command name format
                step_command = command.replace(" ", "_")

                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name=step_command,
                        arguments={}
                    )

                    if response and response.get("success", False):
                        location = response.get("location", "unknown location")
                        return f"Execution continued to {location}"
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else f"Failed to execute {command}"
                        return f"Failed to {command}: {error_msg}"

                except Exception as e:
                    return f"Error executing {command}: {str(e)}"

            elif command == "inspect":
                if not variable:
                    return "Please specify the variable to inspect."

                inspect_params = {
                    "variable": variable
                }

                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="inspect_variable",
                        arguments=inspect_params
                    )

                    if response and "value" in response:
                        value = response["value"]
                        type_info = response.get("type", "unknown type")
                        return f"Variable '{variable}' ({type_info}): {value}"
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to inspect variable"
                        return f"Failed to inspect variable '{variable}': {error_msg}"

                except Exception as e:
                    return f"Error inspecting variable '{variable}': {str(e)}"

            elif command == "stack":
                try:
                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="get_stack_trace",
                        arguments={}
                    )

                    if response and "frames" in response:
                        frames = response["frames"]
                        if not frames:
                            return "Stack trace is empty."

                        result = "Current stack trace:\n\n"
                        for i, frame in enumerate(frames, 1):
                            method = frame.get("method", "unknown method")
                            location = frame.get(
                                "location", "unknown location")
                            result += f"{i}. {method} at {location}\n"

                        return result
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to get stack trace"
                        return f"Failed to get stack trace: {error_msg}"

                except Exception as e:
                    return f"Error getting stack trace: {str(e)}"

            elif command == "threads":
                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="list_threads",
                        arguments={}
                    )

                    if response and "threads" in response:
                        threads = response["threads"]
                        if not threads:
                            return "No threads found."

                        result = "Current threads:\n\n"
                        for i, thread in enumerate(threads, 1):
                            thread_id = thread.get("id", "unknown")
                            name = thread.get("name", "unnamed")
                            status = thread.get("status", "unknown status")
                            result += f"{i}. Thread '{name}' (ID: {thread_id}), Status: {status}\n"

                        return result
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to list threads"
                        return f"Failed to list threads: {error_msg}"

                except Exception as e:
                    return f"Error listing threads: {str(e)}"

            elif command == "attach":
                if not process_id:
                    return "Please specify the process ID to attach to."

                attach_params = {
                    "process_id": process_id
                }

                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="attach_debugger",
                        arguments=attach_params
                    )

                    if response and response.get("success", False):
                        return f"Successfully attached to process {process_id}"
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to attach debugger"
                        return f"Failed to attach debugger: {error_msg}"

                except Exception as e:
                    return f"Error attaching debugger: {str(e)}"

            elif command == "detach":
                try:

                    response = use_mcp_tool(
                        server_name="jdwp",
                        tool_name="detach_debugger",
                        arguments={}
                    )

                    if response and response.get("success", False):
                        return "Successfully detached debugger"
                    else:
                        error_msg = response.get(
                            "error", "Unknown error") if response else "Failed to detach debugger"
                        return f"Failed to detach debugger: {error_msg}"

                except Exception as e:
                    return f"Error detaching debugger: {str(e)}"

            else:
                return f"Unknown debug command: {command}. Try 'help' for a list of available commands."

        except Exception as e:
            return f"Error processing debug command: {str(e)}"

    def _handle_java_debug_help(self) -> str:
        """Provide help information for Java debugging commands.

        Returns:
            Help text for Java debugging
        """
        help_text = """
        Java Debugging Commands:

        1. Launching:
           - "Launch JDIExampleDebuggee"
           - "Run com.baeldung.jdi.JDIExampleDebuggee with arg1 arg2"

        2. Breakpoints:
           - "Set breakpoint in JDIExampleDebuggee.main"
           - "Set breakpoint at line 25 in JDIExampleDebuggee"
           - "List all breakpoints"
           - "Clear breakpoint at line 25 in JDIExampleDebuggee"

        3. Execution Control:
           - "Continue execution"
           - "Step into next instruction"
           - "Step over next instruction"
           - "Step out of current method"

        4. Inspection:
           - "Inspect variable counter"
           - "Show value of myString"
           - "Show stack trace"
           - "List all threads"

        5. Debugger Control:
           - "Attach debugger to process 12345"
           - "Detach debugger"

        You can use these commands in natural language, and I'll interpret your intent.
        """

        return help_text.strip()
