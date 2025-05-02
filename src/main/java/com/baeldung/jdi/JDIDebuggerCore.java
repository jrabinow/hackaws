package com.baeldung.jdi;

import com.sun.jdi.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class JDIDebuggerCore implements DebuggerCore {
    private final VirtualMachine vm;
    private final Map<String, List<Integer>> breakpoints = new HashMap<>();
    private final Map<Long, ThreadReference> threads = new ConcurrentHashMap<>();

    public JDIDebuggerCore(VirtualMachine vm) {
        this.vm = vm;
        // Initialize thread map
        for (ThreadReference thread : vm.allThreads()) {
            threads.put(thread.uniqueID(), thread);
        }
    }

    // Call this from the event loop on ThreadStartEvent
    public void onThreadStart(ThreadStartEvent event) {
        ThreadReference thread = event.thread();
        threads.put(thread.uniqueID(), thread);
    }

    // Call this from the event loop on ThreadDeathEvent
    public void onThreadDeath(ThreadDeathEvent event) {
        ThreadReference thread = event.thread();
        threads.remove(thread.uniqueID());
    }

    @Override
    public List<ThreadReference> listThreads() {
        return new ArrayList<>(threads.values());
    }

    @Override
    public ThreadReference getThread(long threadId) {
        return threads.get(threadId);
    }

    @Override
    public Map<String, Object> variables(long threadId, int frameId) {
        ThreadReference thread = threads.get(threadId);
        if (thread != null && thread.isSuspended()) {
            try {
                if (thread.frameCount() > frameId) {
                    StackFrame frame = thread.frame(frameId);
                    Map<LocalVariable, Value> visibleVariables = frame.getValues(frame.visibleVariables());
                    Map<String, Object> result = new HashMap<>();
                    for (Map.Entry<LocalVariable, Value> entry : visibleVariables.entrySet()) {
                        result.put(entry.getKey().name(), entry.getValue());
                    }
                    return result;
                }
            } catch (IncompatibleThreadStateException | AbsentInformationException e) {
                // Ignore and continue
            }
        }
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> variables(int frameId) {
        // Use the first suspended thread
        for (ThreadReference thread : threads.values()) {
            if (thread.isSuspended()) {
                return variables(thread.uniqueID(), frameId);
            }
        }
        return Collections.emptyMap();
    }

    @Override
    public void setBreakpoints(String source, int[] lines) {
        breakpoints.put(source, Arrays.asList(Arrays.stream(lines).boxed().toArray(Integer[]::new)));
        // Remove existing breakpoints for this source
        List<BreakpointRequest> toDelete = new ArrayList<>();
        for (BreakpointRequest req : vm.eventRequestManager().breakpointRequests()) {
            try {
                if (req.location().sourceName().equals(source)) {
                    toDelete.add(req);
                }
            } catch (AbsentInformationException e) {
                // Ignore breakpoints without source info
            }
        }
        for (BreakpointRequest req : toDelete) {
            vm.eventRequestManager().deleteEventRequest(req);
        }
        // Set new breakpoints
        for (ReferenceType refType : vm.allClasses()) {
            try {
                if (refType.sourceName().equals(source)) {
                    for (int line : lines) {
                        List<Location> locations = refType.locationsOfLine(line);
                        if (!locations.isEmpty()) {
                            BreakpointRequest bpReq = vm.eventRequestManager().createBreakpointRequest(locations.get(0));
                            bpReq.enable();
                        }
                    }
                }
            } catch (AbsentInformationException e) {
                // Ignore classes without line info
            }
        }
    }

    @Override
    public void continueExecution() {
        vm.resume();
    }

    @Override
    public void stepOver() {
        throw new UnsupportedOperationException("Use stepOver(ThreadReference thread) instead");
    }

    public void stepOver(ThreadReference thread) {
        // Remove existing step requests for this thread
        EventRequestManager erm = vm.eventRequestManager();
        List<StepRequest> toDelete = new ArrayList<>();
        for (StepRequest req : erm.stepRequests()) {
            if (req.thread().equals(thread)) {
                toDelete.add(req);
            }
        }
        for (StepRequest req : toDelete) {
            erm.deleteEventRequest(req);
        }
        StepRequest stepRequest = erm.createStepRequest(thread, StepRequest.STEP_LINE, StepRequest.STEP_OVER);
        stepRequest.enable();
    }

    @Override
    public void stepIn() {
        throw new UnsupportedOperationException("Use stepIn(ThreadReference thread) instead");
    }

    public void stepIn(ThreadReference thread) {
        // Remove existing step requests for this thread
        EventRequestManager erm = vm.eventRequestManager();
        List<StepRequest> toDelete = new ArrayList<>();
        for (StepRequest req : erm.stepRequests()) {
            if (req.thread().equals(thread)) {
                toDelete.add(req);
            }
        }
        for (StepRequest req : toDelete) {
            erm.deleteEventRequest(req);
        }
        StepRequest stepRequest = erm.createStepRequest(thread, StepRequest.STEP_LINE, StepRequest.STEP_INTO);
        stepRequest.enable();
    }

    @Override
    public void stepOut() {
        throw new UnsupportedOperationException("Use stepOut(ThreadReference thread) instead");
    }

    public void stepOut(ThreadReference thread) {
        // Remove existing step requests for this thread
        EventRequestManager erm = vm.eventRequestManager();
        List<StepRequest> toDelete = new ArrayList<>();
        for (StepRequest req : erm.stepRequests()) {
            if (req.thread().equals(thread)) {
                toDelete.add(req);
            }
        }
        for (StepRequest req : toDelete) {
            erm.deleteEventRequest(req);
        }
        StepRequest stepRequest = erm.createStepRequest(thread, StepRequest.STEP_LINE, StepRequest.STEP_OUT);
        stepRequest.enable();
    }

    // Additional methods for event handling, etc., can be added as needed
} 