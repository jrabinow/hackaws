package com.baeldung.dap;

import java.io.OutputStream;
import com.baeldung.jdi.DebuggerCore;

public interface DAPAdapter {
    void start(); // Start listening for DAP messages
    void stop();  // Stop the server
    void setDebugger(DebuggerCore debuggerCore); // Inject the debugger core
} 