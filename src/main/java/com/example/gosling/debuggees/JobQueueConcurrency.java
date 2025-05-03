package com.example.gosling.debuggees;

import java.util.*;

public class JobQueueConcurrency {

    public static void main(String[] args) throws InterruptedException {
        JobQueue queue = new JobQueue();
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < 5; i++) {
            threads.add(new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    String job = "job-" + UUID.randomUUID();
                    queue.submit(job);
                    queue.processNext();
                }
            }));
        }

        for (Thread t : threads) t.start();
        for (Thread t : threads) t.join();

        System.out.println("Remaining jobs in queue: " + queue.size());
    }
}

class JobQueue {
    private final List<String> jobs = new ArrayList<>();

    public void submit(String job) {
        if (!jobs.contains(job)) {  // prevent duplicates
            jobs.add(job);
        }
    }

    public void processNext() {
        if (!jobs.isEmpty()) {
            String job = jobs.remove(0);  // simulate processing
            // Optional: simulate variable delay
            if (job.hashCode() % 17 == 0) {
                try {
                    Thread.sleep(1);
                } catch (InterruptedException ignored) {}
            }
        }
    }

    public int size() {
        return jobs.size();
    }
}