# Technical Context: HackAWS Java Debugger

## Technologies Used

### Programming Languages

1. **Java**

   - Version: Java 17 (as specified in build.gradle)
   - Primary language for the MCP server and debugging components
   - Used for JDI (Java Debug Interface) integration

2. **Python**
   - Used for the chat interface and LLM integration
   - Responsible for natural language processing and intent classification
   - Handles communication with the MCP server

### Frameworks & Libraries

1. **Spring Boot**

   - Version: 3.1.0
   - Used for HTTP/SSE protocol implementation
   - Provides web server capabilities
   - Simplifies configuration and dependency injection

2. **LangChain**

   - Used for LLM integration in the Python components
   - Provides tools for agents, prompts, and model interaction
   - Facilitates dynamic tool discovery and usage

3. **MCP Java SDK**

   - Source: `com.github.modelcontextprotocol:java-sdk:main-SNAPSHOT`
   - Provides Model Context Protocol implementation for Java
   - Used for tool definition and server implementation
   - Integrated with Spring Boot for HTTP and SSE protocols

4. **JDI (Java Debug Interface)**

   - Part of the JDK's Java Platform Debugger Architecture (JPDA)
   - Provides interfaces for debugging Java applications
   - Used for attaching to, controlling, and inspecting Java programs

5. **Prompt Toolkit**

   - Python library for building interactive command-line applications
   - Used for the chat interface with features like history and styled prompts

6. **Click**
   - Python library for creating command-line interfaces
   - Used for CLI command handling and output formatting

### Development Tools

1. **Gradle**

   - Build automation tool for Java components
   - Manages dependencies and project configuration
   - Version: As per gradle-wrapper.properties

2. **JUnit**
   - Version: 5.10.0
   - Testing framework for Java components
   - Used for unit testing the MCP server and debugging services

## Development Setup

### Prerequisites

1. Java Development Kit (JDK) 17 or later
2. Python 3.8 or later
3. Gradle

### Project Structure

```
└── hackaws/
    ├── src/
    │   ├── main/
    │   │   ├── java/
    │   │   │   ├── com/
    │   │   │   │   ├── baeldung/
    │   │   │   │   │   ├── dap/
    │   │   │   │   │   └── jdi/
    │   │   │   │   └── example/
    │   │   │   │       └── duck/
    │   │   │   │           ├── debuggee/
    │   │   │   │           ├── debugger/
    │   │   │   │           ├── CommandHandler.java
    │   │   │   │           ├── McpServer.java
    │   │   │   │           └── ProtocolHandler.java
    │   │   └── python/
    │   │       ├── duck/
    │   │       │   ├── __init__.py
    │   │       │   ├── chat_handler.py
    │   │       │   ├── mcp_client.py
    │   │       │   └── provider.py
    │   │       ├── __init__.py
    │   │       ├── main.py
    │   │       ├── mcp.json
    │   │       └── requirements.txt
    ├── gradle/
    ├── build.gradle
    ├── gradlew
    ├── gradlew.bat
    └── mcp-plan.md
```

### Setup Instructions

1. **Java Components:**

   ```bash
   # Build the Java components
   ./gradlew build
   ```

2. **Python Components:**

   ```bash
   # Create a Python virtual environment (optional but recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install Python dependencies
   pip install -r src/main/python/requirements.txt
   ```

3. **Running the Application:**

   ```bash
   # Start the MCP server
   java -cp build/classes/java/main com.example.duck.McpServer

   # In a separate terminal, start the Python chat interface
   cd src/main/python
   python main.py
   ```

## Technical Constraints

1. **JDI Limitations**

   - Can only debug Java applications
   - Requires target application to be launched with debugging enabled or attach to a running JVM
   - Limited information available for native methods

2. **Protocol Handling**

   - Different protocols (stdin, SSE, HTTP) have different capabilities and limitations
   - Real-time updates more challenging with HTTP than with SSE or stdin

3. **LLM Integration**

   - Requires API keys and potentially incurs costs
   - LLM responses can be unpredictable and may require refinement
   - Tool discovery and schema definition needs careful implementation

4. **Cross-Language Communication**
   - Java and Python components communicate via MCP
   - Serialization/deserialization overhead
   - Potential version compatibility issues

## Dependencies

### Java Dependencies

```gradle
dependencies {
    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter:3.1.0'

    // MCP Java SDK
    implementation 'com.github.modelcontextprotocol:java-sdk:main-SNAPSHOT'

    // Testing
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
}
```

### Python Dependencies

Key packages from requirements.txt:

- langchain for LLM integration
- langchain_anthropic and langchain_openai for specific LLM providers
- fastmcp for MCP client implementation
- prompt_toolkit for interactive CLI
- click for command-line interface
- python-dotenv for environment variable management
