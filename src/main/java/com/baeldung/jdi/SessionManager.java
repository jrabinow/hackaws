package com.baeldung.jdi;

import com.sun.jdi.VirtualMachine;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class SessionManager {
    private final Map<String, DebugSession> sessions = new ConcurrentHashMap<>();

    public DebugSession createSession(VirtualMachine vm) {
        String sessionId = UUID.randomUUID().toString();
        JDIDebuggerCore core = new JDIDebuggerCore(vm);
        DebugSession session = new DebugSession(sessionId, core, vm);
        sessions.put(sessionId, session);
        return session;
    }

    public DebugSession getSession(String sessionId) {
        return sessions.get(sessionId);
    }

    public void removeSession(String sessionId) {
        DebugSession session = sessions.remove(sessionId);
        if (session != null) {
            session.close();
        }
    }

    public int getSessionCount() {
        return sessions.size();
    }
} 