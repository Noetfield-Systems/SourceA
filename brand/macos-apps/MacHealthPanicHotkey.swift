import AppKit
import ApplicationServices
import Carbon.HIToolbox
import Foundation

// Mac Health Guard — global PANIC hotkey (⌃⌥⌘S)
// Re-checks Accessibility every few seconds (macOS needs restart after grant).

private var lastPanicAt: TimeInterval = 0
private let panicDebounceSec: TimeInterval = 2.0
private var globalMonitor: Any?
private var localMonitor: Any?
private var accessibilityWasTrusted = false

func logLine(_ msg: String) {
    let home = FileManager.default.homeDirectoryForCurrentUser
    let dir = home.appendingPathComponent(".sina", isDirectory: true)
    try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    let log = dir.appendingPathComponent("mac-health-panic-hotkey.log")
    let line = "\(ISO8601DateFormatter().string(from: Date())) \(msg)\n"
    if let data = line.data(using: .utf8) {
        if FileManager.default.fileExists(atPath: log.path),
           let h = try? FileHandle(forWritingTo: log) {
            h.seekToEndOfFile()
            h.write(data)
            try? h.close()
        } else {
            try? data.write(to: log)
        }
    }
}

func sourceAPath() -> String {
    if let env = ProcessInfo.processInfo.environment["SINA_SOURCEA"], !env.isEmpty {
        return env
    }
    return FileManager.default.homeDirectoryForCurrentUser.path + "/Desktop/SourceA"
}

func accessibilityTrusted(prompt: Bool) -> Bool {
    let key = kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String
    let opts = [key: prompt] as CFDictionary
    return AXIsProcessTrustedWithOptions(opts)
}

func firePanic(trigger: String) {
    let now = Date.timeIntervalSinceReferenceDate
    if now - lastPanicAt < panicDebounceSec {
        logLine("PANIC debounced trigger=\(trigger)")
        return
    }
    lastPanicAt = now

    let root = sourceAPath()
    let script = root + "/scripts/mac_health_emergency_stop_v1.py"
    guard FileManager.default.fileExists(atPath: script) else {
        logLine("FAIL missing script \(script)")
        return
    }
    logLine("PANIC trigger=\(trigger) — spawning stop script")

    let quietFlag = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent(".sina/mac-health-quiet-v1.flag")
    if !FileManager.default.fileExists(atPath: quietFlag.path) {
        let note = "display notification \"Factory frozen — killing agents…\" with title \"⛔ Mac Health PANIC\" sound name \"Basso\""
        let noteProc = Process()
        noteProc.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        noteProc.arguments = ["-e", note]
        try? noteProc.run()
    }

    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
    proc.arguments = [script, "--trigger", trigger, "--fast"]
    var env = ProcessInfo.processInfo.environment
    env["SINA_SOURCEA"] = root
    env["PYTHONPATH"] = root + "/scripts"
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    proc.environment = env
    let log = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent(".sina/mac-health-panic-exec.log")
    if !FileManager.default.fileExists(atPath: log.path) {
        FileManager.default.createFile(atPath: log.path, contents: nil)
    }
    if let h = try? FileHandle(forWritingTo: log) {
        proc.standardOutput = h
        proc.standardError = h
    }
    proc.terminationHandler = { p in
        logLine("PANIC script exit=\(p.terminationStatus)")
    }
    do {
        try proc.run()
    } catch {
        logLine("FAIL exec \(error.localizedDescription)")
    }
}

func matchesPanicHotkey(_ event: NSEvent) -> Bool {
    let flags = event.modifierFlags.intersection([.control, .option, .command, .shift])
    guard flags.contains([.control, .option, .command]) else { return false }
    guard !flags.contains(.shift) else { return false }
    let key = event.charactersIgnoringModifiers?.lowercased() ?? ""
    if key == "s" { return true }
    // Also accept keyCode 1 (S) when modifiers match
    return event.keyCode == 1
}

func installGlobalMonitorIfNeeded() {
    guard globalMonitor == nil else { return }
    guard accessibilityTrusted(prompt: false) else { return }
    globalMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { event in
        if matchesPanicHotkey(event) {
            firePanic(trigger: "hotkey-global")
        }
    }
    logLine("OK NSEvent global monitor LIVE — ⌃⌥⌘S armed")
}

func installLocalMonitorIfNeeded() {
    guard localMonitor == nil else { return }
    localMonitor = NSEvent.addLocalMonitorForEvents(matching: .keyDown) { event in
        if matchesPanicHotkey(event) {
            firePanic(trigger: "hotkey-local")
            return nil
        }
        return event
    }
    logLine("OK NSEvent local monitor installed")
}

var carbonHotKeyRef: EventHotKeyRef?
var carbonHandlerRef: EventHandlerRef?
// Control + Option + Command + S  (STOP) + F19 backup
let carbonHotKeyID = EventHotKeyID(signature: OSType(0x4D4847), id: 1)
let carbonHotKeyF19 = EventHotKeyID(signature: OSType(0x4D4847), id: 2)

func installCarbonHotkey() {
    let handler: EventHandlerUPP = { _, event, _ -> OSStatus in
        var hkID = EventHotKeyID()
        let err = GetEventParameter(
            event,
            EventParamName(kEventParamDirectObject),
            EventParamType(typeEventHotKeyID),
            nil,
            MemoryLayout<EventHotKeyID>.size,
            nil,
            &hkID
        )
        if err == noErr, hkID.id == 1 || hkID.id == 2 {
            firePanic(trigger: hkID.id == 2 ? "hotkey-f19" : "hotkey-carbon")
        }
        return noErr
    }
    var eventType = EventTypeSpec(
        eventClass: OSType(kEventClassKeyboard),
        eventKind: UInt32(kEventHotKeyPressed)
    )
    InstallEventHandler(
        GetApplicationEventTarget(),
        handler,
        1,
        &eventType,
        nil,
        &carbonHandlerRef
    )
    let modifiers = UInt32(controlKey | optionKey | cmdKey)
    let reg = RegisterEventHotKey(
        UInt32(kVK_ANSI_S),
        modifiers,
        carbonHotKeyID,
        GetApplicationEventTarget(),
        0,
        &carbonHotKeyRef
    )
    if reg == noErr {
        logLine("OK Carbon hotkey registered ⌃⌥⌘S")
    } else {
        logLine("WARN Carbon RegisterEventHotKey err=\(reg)")
    }
    var f19Ref: EventHotKeyRef?
    let reg2 = RegisterEventHotKey(
        UInt32(kVK_F19),
        0,
        carbonHotKeyF19,
        GetApplicationEventTarget(),
        0,
        &f19Ref
    )
    if reg2 == noErr {
        logLine("OK Carbon backup hotkey F19 (no modifiers)")
    }
}

let panicFile = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent(".sina/PANIC.now")

func checkPanicFile() {
    guard FileManager.default.fileExists(atPath: panicFile.path) else { return }
    try? FileManager.default.removeItem(at: panicFile)
    firePanic(trigger: "panic-file")
}

func refreshAccessibility() {
    let trusted = accessibilityTrusted(prompt: false)
    if trusted && !accessibilityWasTrusted {
        logLine("accessibility GRANTED — arming global monitor")
        installGlobalMonitorIfNeeded()
    } else if !trusted && accessibilityWasTrusted {
        logLine("WARN accessibility REVOKED")
        globalMonitor = nil
    }
    accessibilityWasTrusted = trusted
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)

let trusted = accessibilityTrusted(prompt: false)
accessibilityWasTrusted = trusted
logLine("start pid=\(ProcessInfo.processInfo.processIdentifier) accessibility=\(trusted)")

installLocalMonitorIfNeeded()
installCarbonHotkey()
if trusted {
    installGlobalMonitorIfNeeded()
} else {
    logLine("WAITING: enable Mac Health Panic in Accessibility — will auto-arm within 3s")
}

Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { _ in
    refreshAccessibility()
    checkPanicFile()
}

app.run()
