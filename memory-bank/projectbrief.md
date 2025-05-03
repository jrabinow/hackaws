# Project Brief: HackAWS Java Debugger

## Project Overview

HackAWS is a debugging tool for Java applications that leverages the Model Context Protocol (MCP) to provide a conversational debugging experience. The project combines a Java-based MCP server with a Python-based chat interface, allowing developers to debug Java applications using natural language.

## Core Objectives

1. Implement an MCP server that can communicate via different protocols (stdin, SSE, HTTP)
2. Create a debugging interface for Java applications
3. Allow users to interact with the debugger using natural language
4. Provide simulated debugging capabilities (breakpoints, stepping, variable inspection)
5. Integrate with LLMs to provide a conversational debugging experience

## Key Requirements

- Support for different communication protocols (stdin, SSE, HTTP)
- Ability to launch and debug Java applications
- Natural language processing to interpret debugging commands
- Integration with JDI (Java Debug Interface) for actual debugging capabilities
- LLM integration for conversational debugging
- Extensible architecture for future enhancements

## Project Scope

The project is focused on creating a functional debugging tool for Java applications with the following capabilities:

- Setting and managing breakpoints
- Stepping through code execution
- Inspecting variables and stack traces
- Analyzing program state
- Providing debugging assistance through natural language
