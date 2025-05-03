# System Patterns: HackAWS Java Debugger

## System Architecture

The HackAWS Java Debugger follows a layered architecture that separates concerns and allows for flexibility in implementation:

```
┌─────────────────────────────────────────┐
│             Chat Interface              │
│         (Python, LangChain, CLI)        │
├─────────────────────────────────────────┤
│             MCP Integration             │
│      (MCP Client, Tool Discovery)       │
├─────────────────────────────────────────┤
│              MCP Server                 │
│     (Java, Protocol Handlers, JSON)     │
├─────────────────────────────────────────┤
│           Debugging Services            │
│    (JDI, Command Handling, Simulation)  │
└─────────────────────────────────────────┘
```

### Key Components

1. **Chat Interface Layer**:

   - Implemented in Python
   - Uses LangChain for LLM integration
   - Provides CLI interaction with users
   - Interprets natural language using intent classification

2. **MCP Integration Layer**:

   - Manages communication with MCP servers
   - Discovers available tools and exposes them to the LLM
   - Translates between chat requests and MCP tool calls

3. **MCP Server Layer**:

   - Implements the Model Context Protocol
   - Supports multiple communication protocols (stdin, SSE, HTTP)
   - Handles serialization/deserialization of commands and responses

4. **Debugging Services Layer**:
   - Integrates with Java Debug Interface (JDI)
   - Manages program execution control
   - Provides breakpoint management, variable inspection, etc.
   - Currently includes simulated functionality for demonstration purposes

## Key Technical Decisions

1. **Dual-Language Implementation**:

   - Python for the chat interface and LLM integration
   - Java for the debugging backend and MCP server
   - Communication via the Model Context Protocol

2. **Protocol Flexibility**:

   - Support for multiple communication protocols
   - Protocol abstraction through the ProtocolHandler interface
   - Easy extension to support additional protocols

3. **Command Pattern**:

   - Use of the Command pattern for handling debug operations
   - Centralized command handling in CommandHandler class
   - Extensible framework for adding new commands

4. **Simulation First Approach**:

   - Initial implementation with simulated debugging responses
   - Allows for testing the interface without JDI integration
   - Clean separation that will allow easy replacement with real functionality

5. **MCP Integration**:
   - Use of the Model Context Protocol for AI integration
   - Standard interface for tool discovery and usage
   - Expandable to incorporate additional AI capabilities

## Design Patterns in Use

1. **Command Pattern**:

   - Used for encapsulating debugging operations
   - Allows for centralized handling and processing of commands
   - Facilitates addition of new debugging commands

2. **Strategy Pattern**:

   - Used for protocol handling
   - Different strategies for stdin, SSE, and HTTP protocols
   - Selection of appropriate strategy at runtime

3. **Observer Pattern**:

   - Implicit in event handling for debugging events
   - Allows for notifications when program state changes
   - Facilitates real-time updates to the user interface

4. **Factory Pattern**:

   - Used for creating appropriate handlers and services
   - Centralizes creation logic
   - Enhances maintainability and testability

5. **Singleton Pattern**:
   - Used for certain services that should exist only once
   - Ensures consistent state across the application
   - Controls access to shared resources

## Component Relationships

1. **Chat Interface ↔ MCP Integration**:

   - Chat interface uses MCP client to discover and call tools
   - Intent classification in ChatHandler directs to appropriate MCP tools
   - Responses from MCP calls are formatted and presented to the user

2. **MCP Integration ↔ MCP Server**:

   - Communication via the Model Context Protocol
   - MCP client sends requests to the server
   - Server processes requests and returns responses

3. **MCP Server ↔ Debugging Services**:

   - MCP server translates between MCP protocol and internal commands
   - CommandHandler processes commands and interacts with debugging services
   - Results from debugging operations are formatted as MCP responses

4. **Debugging Services ↔ Java Program**:
   - Currently simulated for demonstration
   - Will use JDI to interact with the target Java program
   - Provides breakpoint management, stepping, inspection, etc.
