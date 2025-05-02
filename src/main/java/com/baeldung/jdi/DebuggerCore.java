package com.baeldung.jdi;

import java.util.Map;

public interface DebuggerCore {
    void setBreakpoints(String source, int[] lines);
    void continueExecution();
    void stepOver();
    void stepIn();
    void stepOut();
    Map<String, Object> variables(int frameId);
    // ... other methods as needed
} 