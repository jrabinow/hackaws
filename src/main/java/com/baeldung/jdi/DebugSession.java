package com.baeldung.jdi;

import com.sun.jdi.VirtualMachine;
import java.time.Instant;
import lombok.Data;

@Data
public class DebugSession {
    private final String sessionId;
    private final JDIDebuggerCore debuggerCore;
    private final VirtualMachine vm;
    private final Instant createdAt;
    private Instant lastActivity;
    private final String userId;
    private SessionState state;

    public DebugSession(String sessionId, JDIDebuggerCore debuggerCore, VirtualMachine vm, String userId) {
        this.sessionId = sessionId;
        this.debuggerCore = debuggerCore;
        this.vm = vm;
        this.createdAt = Instant.now();
        this.lastActivity = this.createdAt;
        this.userId = userId;
        this.state = SessionState.ACTIVE;
    }

    public void updateActivity() { this.lastActivity = Instant.now(); }

    public void close() {
        setState(SessionState.TERMINATED);
        if (vm != null) {
            try {
                vm.dispose();
            } catch (Exception e) {
                // Ignore any exception during dispose
            }
        }
    }
} 
