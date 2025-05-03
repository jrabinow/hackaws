package com.example.gosling;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.tool.Tool;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service providing tools, resources, and prompts for the debug MCP server.
 * This demonstrates a simple implementation of MCP tools using Spring AI.
 */
public class DebugToolService {
    
    // In-memory storage for our "variables" - simulating a debugging environment
    private final Map<String, Object> variables = new ConcurrentHashMap<>();

    /**
     * Get the inspect variable tool.
     * This tool inspects a variable in the debug context.
     */
    public Tool getInspectVariableTool() {
        return Tool.builder("inspect_variable")
            .description("Inspect the value of a variable in the current debug context")
            .parameter("name", String.class, "Name of the variable to inspect")
            .action(params -> {
                String name = (String) params.get("name");
                log.info("Inspecting variable: {}", name);
                
                if (variables.containsKey(name)) {
                    Object value = variables.get(name);
                    String type = value != null ? value.getClass().getSimpleName() : "null";
                    return "Variable '" + name + "' = " + value + " (Type: " + type + ")";
                } else {
                    return "Variable '" + name + "' not found in current context";
                }
            })
            .build();
    }
    
    /**
     * Get the set variable tool.
     * This tool sets a variable in the debug context.
     */
    public Tool getSetVariableTool() {
        return Tool.builder("set_variable")
            .description("Set the value of a variable in the current debug context")
            .parameter("name", String.class, "Name of the variable to set")
            .parameter("value", String.class, "String representation of the value to set")
            .action(params -> {
                String name = (String) params.get("name");
                String value = (String) params.get("value");
                
                log.info("Setting variable: {} = {}", name, value);
                variables.put(name, value);
                
                return "Variable '" + name + "' set to '" + value + "'";
            })
            .build();
    }
    
    /**
     * Get all debug variables as a document for resource access.
     * This demonstrates how to expose a resource in the MCP context.
     */
    public Document getDebugVariablesDocument() {
        log.info("Retrieving all variables as a document");
        
        StringBuilder builder = new StringBuilder();
        builder.append("Debug Variables:\n\n");
        
        if (variables.isEmpty()) {
            builder.append("No variables in current context.");
        } else {
            variables.forEach((name, value) -> {
                String type = value != null ? value.getClass().getSimpleName() : "null";
                builder.append(String.format("- %s = %s (Type: %s)\n", name, value, type));
            });
        }
        
        return new Document(builder.toString(), Map.of("uri", "debug://variables"));
    }
    
    /**
     * Debug assistance functionality.
     * This would typically use an LLM for generating responses.
     */
    public String generateDebugAssistance(String code, String issue) {
        log.info("Generating debug assistance for issue: {}", issue);
        
        // In a real implementation, this might use an LLM or some analysis logic
        // For this example, we'll just return a simulated response
        return "## Debug Analysis\n\n"
            + "I've analyzed your code and the reported issue:\n\n"
            + "```java\n" + code + "\n```\n\n"
            + "### Issue Description\n"
            + issue + "\n\n"
            + "### Potential Solutions\n"
            + "- Check for null pointer exceptions in your code\n"
            + "- Verify that all variables are properly initialized\n"
            + "- Ensure proper exception handling";
    }
    
    /**
     * Helper method to get all tools provided by this service.
     */
    public List<Tool> getTools() {
        return List.of(
            getInspectVariableTool(),
            getSetVariableTool()
        );
    }
}
