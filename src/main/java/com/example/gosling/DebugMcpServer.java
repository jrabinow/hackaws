package com.example.gosling;

import java.util.Map;
import java.util.HashMap;
import java.util.Scanner;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.ArrayList;
import java.util.List;

/**
 * A Model Context Protocol server implementation for debugging Java applications.
 * Supports multiple transport methods: STDIO, HTTP Streaming, and Server-Sent Events (SSE).
 */
public class DebugMcpServer {
    // Transport method options
    public enum TransportMethod {
        STDIO,           // Standard IO stream transport
        HTTP_STREAMING,  // HTTP streaming transport
        SSE              // Server-sent events transport
    }
    
    private final DebugToolService toolService;
    private boolean running = false;
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Map<String, Object> sseEmitters = new ConcurrentHashMap<>();
    
    /**
     * Constructor with the debug tool service.
     */
    public DebugMcpServer() {
        this.toolService = new DebugToolService();
    }
    
    /**
     * Main method to start the server.
     */
    public static void main(String[] args) {
        // Determine transport method from args
        TransportMethod method = TransportMethod.STDIO; // Default to STDIO
        
        if (args.length > 0) {
            try {
                method = TransportMethod.valueOf(args[0].toUpperCase());
            } catch (IllegalArgumentException e) {
                System.err.println("Invalid transport method: " + args[0]);
                System.err.println("Valid options: STDIO, HTTP_STREAMING, SSE");
                System.exit(1);
            }
        }
        
        // Start server with selected transport method
        switch (method) {
            case STDIO:
                runStandaloneServer();
                break;
            case HTTP_STREAMING:
            case SSE:
                System.out.println("Starting server with " + method + " transport...");
                System.out.println("This would normally start a Spring Boot application.");
                System.out.println("To use STDIO transport, run with: STDIO");
                break;
        }
    }
    
    /**
     * Run the server with Spring Boot integration.
     * This enables HTTP Streaming and SSE transport.
     * 
     * Note: This is a placeholder that would normally use Spring Boot.
     */
    public static void runSpringBootServer(String[] args) {
        System.out.println("Starting Debug MCP Server with Spring Boot...");
        System.out.println("This would normally use SpringApplication.run()");
        System.out.println("Debug MCP Server running with Spring Boot.");
        System.out.println("HTTP Streaming API: http://localhost:8080/mcp/streaming");
        System.out.println("SSE API: http://localhost:8080/mcp/events");
    }
    
    /**
     * Run the server in standalone mode with STDIO transport.
     */
    public static void runStandaloneServer() {
        System.out.println("Starting Debug MCP Server in standalone mode with STDIO transport...");
        DebugMcpServer server = new DebugMcpServer();
        server.startStdioTransport();
    }
    
    /**
     * Start the MCP server with STDIO transport.
     * This is a simple implementation that reads from stdin and writes to stdout.
     */
    public void startStdioTransport() {
        System.out.println("Starting Debug MCP Server with STDIO transport...");
        running = true;
        
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Server ready. Listening for commands...");
            System.out.println("Debug MCP Server available tools:");
            for (DebugToolService.ToolDescriptor tool : toolService.getToolDescriptors()) {
                System.out.println("- " + tool.getName() + ": " + tool.getDescription());
            }
            
            while (running && scanner.hasNextLine()) {
                String input = scanner.nextLine();
                if (input.equals("exit")) {
                    running = false;
                    continue;
                }
                
                try {
                    // Parse the input as a JSON object
                    Map<String, Object> request = parseJson(input);
                    String response = handleRequest(request);
                    System.out.println(response);
                } catch (Exception e) {
                    System.err.println("Error processing request: " + e.getMessage());
                    e.printStackTrace();
                    
                    try {
                        System.out.println(createErrorResponse(e.getMessage()));
                    } catch (Exception ex) {
                        System.err.println("Failed to create error response: " + ex.getMessage());
                    }
                }
            }
        }
        
        System.out.println("Debug MCP Server stopped.");
    }
    
    /**
     * Stop the server.
     */
    public void stop() {
        running = false;
        executor.shutdown();
    }
    
    /**
     * Handle a request from the client.
     * This is a simple implementation that supports various debugging tools.
     */
    private String handleRequest(Map<String, Object> request) throws Exception {
        String toolName = (String) request.get("tool");
        Map<String, Object> arguments = (Map<String, Object>) request.get("arguments");
        
        if (toolName == null) {
            return createErrorResponse("No tool specified");
        }
        
        if (arguments == null) {
            arguments = new HashMap<>();
        }
        
        String result;
        switch (toolName) {
            case "inspect_variable":
                String variableName = (String) arguments.get("name");
                result = toolService.inspectVariable(variableName);
                break;
            case "set_variable":
                String name = (String) arguments.get("name");
                String value = (String) arguments.get("value");
                result = toolService.setVariable(name, value);
                break;
            case "get_variables":
                result = toolService.getDebugVariables();
                break;
            case "debug_assistance":
                String code = (String) arguments.get("code");
                String issue = (String) arguments.get("issue");
                result = toolService.generateDebugAssistance(code, issue);
                break;
            default:
                return createErrorResponse("Unknown tool: " + toolName);
        }
        
        return createSuccessResponse(result);
    }
    
    /**
     * Create a success response in JSON format.
     */
    private String createSuccessResponse(String result) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        sb.append("\"status\": \"success\",");
        sb.append("\"result\": ");
        // If result is already JSON, don't quote it
        if (result.trim().startsWith("{") || result.trim().startsWith("[")) {
            sb.append(result);
        } else {
            sb.append("\"").append(escapeJsonString(result)).append("\"");
        }
        sb.append("}");
        return sb.toString();
    }
    
    /**
     * Create an error response in JSON format.
     */
    private String createErrorResponse(String errorMessage) {
        return "{\"status\": \"error\", \"error\": \"" + escapeJsonString(errorMessage) + "\"}";
    }
    
    /**
     * Escape special characters for JSON string.
     */
    private String escapeJsonString(String input) {
        if (input == null) {
            return "";
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            char ch = input.charAt(i);
            switch (ch) {
                case '"':
                    sb.append("\\\"");
                    break;
                case '\\':
                    sb.append("\\\\");
                    break;
                case '\b':
                    sb.append("\\b");
                    break;
                case '\f':
                    sb.append("\\f");
                    break;
                case '\n':
                    sb.append("\\n");
                    break;
                case '\r':
                    sb.append("\\r");
                    break;
                case '\t':
                    sb.append("\\t");
                    break;
                default:
                    if (ch < ' ') {
                        String hex = "000" + Integer.toHexString(ch);
                        sb.append("\\u").append(hex.substring(hex.length() - 4));
                    } else {
                        sb.append(ch);
                    }
            }
        }
        return sb.toString();
    }
    
    /**
     * Very simple JSON parser for demonstration purposes.
     * In a real implementation, you would use a proper JSON library.
     */
    private Map<String, Object> parseJson(String json) {
        Map<String, Object> result = new HashMap<>();
        
        // This is a very simplistic parser that only handles a subset of JSON
        // For a real implementation, use a proper JSON library
        
        // Extract the tool name
        int toolStart = json.indexOf("\"tool\"");
        if (toolStart >= 0) {
            int colonPos = json.indexOf(':', toolStart);
            int startQuote = json.indexOf('"', colonPos);
            int endQuote = json.indexOf('"', startQuote + 1);
            if (startQuote >= 0 && endQuote >= 0) {
                String toolName = json.substring(startQuote + 1, endQuote);
                result.put("tool", toolName);
            }
        }
        
        // Extract arguments
        int argsStart = json.indexOf("\"arguments\"");
        if (argsStart >= 0) {
            Map<String, Object> args = new HashMap<>();
            
            // Find opening brace of arguments object
            int openBrace = json.indexOf('{', argsStart);
            if (openBrace >= 0) {
                // Find closing brace of arguments object
                int closeBrace = findClosingBrace(json, openBrace);
                if (closeBrace >= 0) {
                    String argsJson = json.substring(openBrace + 1, closeBrace);
                    
                    // Simple key-value parser
                    int pos = 0;
                    while (pos < argsJson.length()) {
                        // Find key
                        int keyStart = argsJson.indexOf('"', pos);
                        if (keyStart < 0) break;
                        
                        int keyEnd = argsJson.indexOf('"', keyStart + 1);
                        if (keyEnd < 0) break;
                        
                        String key = argsJson.substring(keyStart + 1, keyEnd);
                        
                        // Find value
                        int colon = argsJson.indexOf(':', keyEnd);
                        if (colon < 0) break;
                        
                        int valueStart = argsJson.indexOf('"', colon);
                        if (valueStart < 0) break;
                        
                        int valueEnd = argsJson.indexOf('"', valueStart + 1);
                        if (valueEnd < 0) break;
                        
                        String value = argsJson.substring(valueStart + 1, valueEnd);
                        
                        args.put(key, value);
                        pos = valueEnd + 1;
                    }
                }
            }
            
            result.put("arguments", args);
        }
        
        return result;
    }
    
    /**
     * Find the position of the closing brace that matches the opening brace at the given position.
     */
    private int findClosingBrace(String json, int openBracePos) {
        int count = 1;
        for (int i = openBracePos + 1; i < json.length(); i++) {
            char ch = json.charAt(i);
            if (ch == '{') {
                count++;
            } else if (ch == '}') {
                count--;
                if (count == 0) {
                    return i;
                }
            }
        }
        return -1;
    }

    /**
     * Quick example usage of the server.
     */
    public static void runExample() {
        System.out.println("Running Debug MCP Server example...");
        
        DebugToolService service = new DebugToolService();
        
        // Set some example variables
        service.setVariable("counter", "42");
        service.setVariable("message", "Hello, MCP!");
        service.setVariable("active", "true");
        
        // Inspect variables
        System.out.println(service.inspectVariable("counter"));
        System.out.println(service.inspectVariable("unknown"));
        
        // Get all variables
        System.out.println(service.getDebugVariables());
        
        // Example of debug assistance
        String code = "public void example() { String s = null; s.length(); }";
        String issue = "NullPointerException at line 1";
        System.out.println(service.generateDebugAssistance(code, issue));
        
        System.out.println("Example complete.");
    }
}
