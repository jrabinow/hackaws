package com.baeldung.jdi;

import java.util.Map;
import java.util.List;
import com.sun.jdi.ThreadReference;

public interface DebuggerCore {
    void setBreakpoints(String source, int[] lines);
    void continueExecution();
    void stepOver();
    void stepIn();
    void stepOut();
    Map<String, Object> variables(int frameId);

    // Multithreading support
    List<ThreadReference> listThreads();
    ThreadReference getThread(long threadId);
    Map<String, Object> variables(long threadId, int frameId);
} 