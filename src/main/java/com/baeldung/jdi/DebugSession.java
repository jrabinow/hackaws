package com.baeldung.jdi;

import com.sun.jdi.VirtualMachine;

public class DebugSession {
    private final String sessionId;
    private final JDIDebuggerCore debuggerCore;
    private final VirtualMachine vm;

    public DebugSession(String sessionId, JDIDebuggerCore debuggerCore, VirtualMachine vm) {
        this.sessionId = sessionId;
        this.debuggerCore = debuggerCore;
        this.vm = vm;
    }

    public String getSessionId() {
        return sessionId;
    }

    public JDIDebuggerCore getDebuggerCore() {
        return debuggerCore;
    }

    public VirtualMachine getVirtualMachine() {
        return vm;
    }

    public void close() {
        if (vm != null) {
            try {
                vm.dispose();
            } catch (Exception e) {
                // Ignore any exception during dispose
            }
        }
    }
} 