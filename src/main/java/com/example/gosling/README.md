# DebugMcpServer

A simple implementation of a Model Context Protocol (MCP) server with debugging capabilities for Java applications.

## Overview

This implementation demonstrates how to create an MCP server with multiple transport methods:

1. **STDIO**: Simple standard input/output streaming transport
2. **HTTP Streaming**: (Placeholder implementation) HTTP streaming transport
3. **SSE**: (Placeholder implementation) Server-Sent Events transport

It provides:

1. **Tools**: Functionality for inspecting and manipulating variables in a debug context
2. **Resources**: Data sources that provide information about the debug state
3. **Prompts**: Templates for generating debugging assistance

## Components

### DebugMcpServer

The main server class that sets up the MCP server with multiple transport options:

- STDIO transport for command-line usage
- HTTP streaming transport (placeholder)
- Server-Sent Events (SSE) transport (placeholder)

### DebugToolService

Service class that implements the debugging functionality:

#### Tools

1. **inspect_variable**: Examines the value and type of a variable in the current debug context

   ```json
   {
     "tool": "inspect_variable",
     "arguments": {
       "name": "variableName"
     }
   }
   ```

2. **set_variable**: Sets the value of a variable in the current debug context

   ```json
   {
     "tool": "set_variable",
     "arguments": {
       "name": "variableName",
       "value": "newValue"
     }
   }
   ```

3. **get_variables**: Returns the current state of all variables in the debug context

   ```json
   {
     "tool": "get_variables"
   }
   ```

4. **debug_assistance**: Generates debugging assistance for code issues
   ```json
   {
     "tool": "debug_assistance",
     "arguments": {
       "code": "public void example() { String s = null; s.length(); }",
       "issue": "NullPointerException at line 1"
     }
   }
   ```

### DebugMcpServerExample

Example class showing how to use the server with various transport methods and direct API usage.

## Usage

### Running with STDIO Transport (Default)

```bash
java -cp <classpath> com.example.gosling.DebugMcpServerExample stdio
```

### Running with HTTP Streaming Transport

```bash
java -cp <classpath> com.example.gosling.DebugMcpServerExample http
```

### Running with Server-Sent Events (SSE) Transport

```bash
java -cp <classpath> com.example.gosling.DebugMcpServerExample sse
```

### Running the Example

```bash
java -cp <classpath> com.example.gosling.DebugMcpServerExample example
```

### Direct API Usage

```java
// Create a debug tool service
DebugToolService service = new DebugToolService();

// Set a variable
service.setVariable("counter", "42");

// Inspect the variable
String result = service.inspectVariable("counter");
System.out.println(result);

// Get all variables
String allVars = service.getDebugVariables();
System.out.println(allVars);

// Get debugging assistance
String code = "public void example() { String s = null; s.length(); }";
String issue = "NullPointerException at line 1";
String assistance = service.generateDebugAssistance(code, issue);
System.out.println(assistance);
```

## Client Usage

### Setting a Variable

```json
{
  "tool": "set_variable",
  "arguments": {
    "name": "counter",
    "value": "42"
  }
}
```

### Inspecting a Variable

```json
{
  "tool": "inspect_variable",
  "arguments": {
    "name": "counter"
  }
}
```

### Getting All Variables

```json
{
  "tool": "get_variables"
}
```

### Using Debug Assistance

```json
{
  "tool": "debug_assistance",
  "arguments": {
    "code": "public void example() { String s = null; s.length(); }",
    "issue": "NullPointerException at line 1"
  }
}
```

## Implementation Details

### JSON Processing

This implementation includes a simple, dependency-free JSON parser and serializer to minimize external dependencies. In a production environment, you would use a proper JSON library such as Jackson or Gson.

### Transport Methods

1. **STDIO**: The fully implemented transport method uses standard input and output streams for communication.

2. **HTTP Streaming**: A placeholder for Spring Boot integration that would use HTTP streaming responses.

3. **Server-Sent Events (SSE)**: A placeholder for Spring Boot integration that would use Server-Sent Events for asynchronous communication.

## Extending

To extend this server with additional functionality:

1. Add new tool methods to the `DebugToolService` class
2. Add tool descriptors in the `getToolDescriptors()` method
3. Update the `handleRequest()` method in `DebugMcpServer` to handle the new tools

## Dependencies

- Java 11+
- No external dependencies (pure Java implementation)
