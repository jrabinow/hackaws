# Java JDI Debugger

## Prerequisites
- Java 21+
- Gradle (wrapper included)

## Build

```
./gradlew build
```

or to build a runnable JAR:

```
./gradlew jar
```

## Run

### With Gradle

```
./gradlew run
```

### Standalone (no build tool required)

After building the JAR, you can run it directly:

```
java -jar build/libs/hackathon_jdi_debugger-1.0.0.jar
```

This will launch the main class: `com.baeldung.jdi.JDIExampleDebugger`.

---

(Old Makefile-based instructions are obsolete and have been removed.)

https://stackoverflow.com/questions/18093928/what-does-could-not-find-or-load-main-class-mean  
https://stackoverflow.com/questions/2096283/including-jars-in-classpath-on-commandline-javac-or-apt

IRC: https://web.libera.chat/gamja/ channel #lih
