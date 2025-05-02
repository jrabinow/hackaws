package com.baeldung.jdi;

import com.sun.jdi.VirtualMachine;
import com.sun.jdi.event.*;

public class JDIExampleDebugger {
    private Class debugClass;
    private int[] breakPointLines;

    public Class getDebugClass() { return debugClass; }
    public void setDebugClass(Class debugClass) { this.debugClass = debugClass; }
    public int[] getBreakPointLines() { return breakPointLines; }
    public void setBreakPointLines(int[] breakPointLines) { this.breakPointLines = breakPointLines; }

    public VirtualMachine connectAndLaunchVM() throws Exception {
        var launchingConnector = com.sun.jdi.Bootstrap.virtualMachineManager().defaultConnector();
        var arguments = launchingConnector.defaultArguments();
        arguments.get("main").setValue(debugClass.getName());
        // Set classpath for debuggee JVM to this JAR
        String jarPath = new java.io.File(JDIExampleDebugger.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getPath();
        String options = "-cp " + jarPath;
        arguments.get("options").setValue(options);
        return launchingConnector.launch(arguments);
    }

    public void enableClassPrepareRequest(VirtualMachine vm) {
        var classPrepareRequest = vm.eventRequestManager().createClassPrepareRequest();
        classPrepareRequest.addClassFilter(debugClass.getName());
        classPrepareRequest.enable();
    }

    public void displayVariables(JDIDebuggerCore debuggerCore) {
        var variables = debuggerCore.variables(0);
        if (!variables.isEmpty()) {
            System.out.println("Variables at top frame > ");
            for (var entry : variables.entrySet()) {
                System.out.println(entry.getKey() + " = " + entry.getValue());
            }
        }
    }

    public static void main(String[] args) throws Exception {
        JDIExampleDebugger debuggerInstance = new JDIExampleDebugger();
        debuggerInstance.setDebugClass(JDIExampleDebuggee.class);
        int[] breakPoints = {6, 9};
        debuggerInstance.setBreakPointLines(breakPoints);
        VirtualMachine vm = null;
        SessionManager sessionManager = new SessionManager();
        DebugSession session = null;
        try {
            vm = debuggerInstance.connectAndLaunchVM();
            debuggerInstance.enableClassPrepareRequest(vm);
            session = sessionManager.createSession(vm);
            JDIDebuggerCore debuggerCore = session.getDebuggerCore();
            EventSet eventSet = null;
            while ((eventSet = vm.eventQueue().remove()) != null) {
                for (Event event : eventSet) {
                    if (event instanceof ClassPrepareEvent) {
                        String source = ((ClassPrepareEvent)event).referenceType().sourceName();
                        debuggerCore.setBreakpoints(source, debuggerInstance.getBreakPointLines());
                    }
                    if (event instanceof BreakpointEvent) {
                        event.request().disable();
                        debuggerInstance.displayVariables(debuggerCore);
                        debuggerCore.stepOver(((BreakpointEvent)event).thread());
                    }
                    if (event instanceof StepEvent) {
                        debuggerInstance.displayVariables(debuggerCore);
                    }
                    vm.resume();
                }
            }
        } catch (com.sun.jdi.VMDisconnectedException e) {
            System.out.println("Virtual Machine is disconnected.");
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (session != null) {
                sessionManager.removeSession(session.getSessionId());
            }
        }
    }
}
