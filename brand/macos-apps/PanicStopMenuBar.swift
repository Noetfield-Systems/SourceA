import AppKit
import ApplicationServices
import Carbon.HIToolbox
import Foundation

// Panic Stop — menu bar app (⛔). Global hotkeys + click-to-stop.
// Shortcuts: ⌃⌘P · ⌃⌥⌘S · click menu bar ⛔

func logLine(_ msg: String) {
    let home = FileManager.default.homeDirectoryForCurrentUser
    let dir = home.appendingPathComponent(".sina", isDirectory: true)
    try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    let log = dir.appendingPathComponent("mac-health-panic-hotkey.log")
    let line = "\(ISO8601DateFormatter().string(from: Date())) [menubar] \(msg)\n"
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
    if let env = ProcessInfo.processInfo.environment["SINA_SOURCEA"], !env.isEmpty { return env }
    return FileManager.default.homeDirectoryForCurrentUser.path + "/Desktop/SourceA"
}

private var lastPanic: TimeInterval = 0

func firePanic(_ trigger: String) -> String {
    let now = Date.timeIntervalSinceReferenceDate
    if now - lastPanic < 2.0 { return "Debounced — wait 2s" }
    lastPanic = now
    logLine("PANIC trigger=\(trigger)")
    let quietFlag = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent(".sina/mac-health-quiet-v1.flag")
    let basso = "/System/Library/Sounds/Basso.aiff"
    if !FileManager.default.fileExists(atPath: quietFlag.path),
       FileManager.default.fileExists(atPath: basso) {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/afplay")
        p.arguments = [basso]
        try? p.run()
    }
    let uid = getuid()
    for label in ["com.sourcea.autorun-worker", "com.sourcea.hub", "com.sourcea.g7-governance-self-heal"] {
        let lc = Process()
        lc.executableURL = URL(fileURLWithPath: "/bin/launchctl")
        lc.arguments = ["bootout", "gui/\(uid)/\(label)"]
        try? lc.run()
        lc.waitUntilExit()
    }
    let root = sourceAPath()
    let script = root + "/scripts/mac_health_emergency_stop_v1.py"
    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
    proc.arguments = [script, "--trigger", trigger, "--fast", "--json"]
    var env = ProcessInfo.processInfo.environment
    env["SINA_SOURCEA"] = root
    env["PYTHONPATH"] = root + "/scripts"
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    proc.environment = env
    let pipe = Pipe()
    proc.standardOutput = pipe
    proc.standardError = pipe
    try? proc.run()
    proc.waitUntilExit()
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
        return (json["founder_line"] as? String) ?? (json["summary"] as? String) ?? "Done"
    }
    return String(data: data, encoding: .utf8) ?? "Done"
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var globalMonitor: Any?
    var carbonRefs: [EventHotKeyRef?] = []

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        if let btn = statusItem.button {
            btn.title = "STOP"
            btn.toolTip = "PANIC STOP — click or ⌃⌘P"
        }
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "PANIC STOP now", action: #selector(panicClick), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit Panic Stop", action: #selector(quitApp), keyEquivalent: "q"))
        statusItem.menu = menu

        let trusted = AXIsProcessTrustedWithOptions(
            [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        )
        logLine("start accessibility=\(trusted)")

        installGlobalKeyMonitor()
        installCarbonHotkeys()

        Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            self.checkPanicFile()
            if !AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: false] as CFDictionary),
               self.globalMonitor == nil {
                logLine("WARN still no Accessibility — enable Panic Stop in System Settings")
            } else if self.globalMonitor == nil {
                self.installGlobalKeyMonitor()
            }
        }
    }

    @objc func panicClick() {
        DispatchQueue.global(qos: .userInitiated).async {
            let msg = firePanic("menubar-click")
            DispatchQueue.main.async {
                let alert = NSAlert()
                alert.messageText = "⛔ STOPPED"
                alert.informativeText = msg
                alert.runModal()
            }
        }
    }
    @objc func quitApp() { NSApp.terminate(nil) }

    func installGlobalKeyMonitor() {
        guard AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: false] as CFDictionary) else { return }
        guard globalMonitor == nil else { return }
        globalMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { event in
            let f = event.modifierFlags.intersection([.control, .option, .command, .shift])
            let key = event.charactersIgnoringModifiers?.lowercased() ?? ""
            if f.contains([.control, .command]) && key == "p" && !f.contains(.option) {
                firePanic("hotkey-ctrl-cmd-p")
            } else if f.contains([.control, .option, .command]) && key == "s" {
                firePanic("hotkey-ctrl-alt-cmd-s")
            }
        }
        logLine("OK NSEvent global monitor — ⌃⌘P · ⌃⌥⌘S")
    }

    func installCarbonHotkeys() {
        let handler: EventHandlerUPP = { _, event, _ -> OSStatus in
            var hk = EventHotKeyID()
            GetEventParameter(event, EventParamName(kEventParamDirectObject), EventParamType(typeEventHotKeyID), nil, MemoryLayout<EventHotKeyID>.size, nil, &hk)
            if hk.id == 1 { firePanic("hotkey-carbon-p") }
            if hk.id == 2 { firePanic("hotkey-carbon-s") }
            return noErr
        }
        var ref: EventHandlerRef?
        var spec = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
        InstallEventHandler(GetApplicationEventTarget(), handler, 1, &spec, nil, &ref)
        var r1: EventHotKeyRef?
        var r2: EventHotKeyRef?
        RegisterEventHotKey(UInt32(kVK_ANSI_P), UInt32(controlKey | cmdKey), EventHotKeyID(signature: 0x504E43, id: 1), GetApplicationEventTarget(), 0, &r1)
        RegisterEventHotKey(UInt32(kVK_ANSI_S), UInt32(controlKey | optionKey | cmdKey), EventHotKeyID(signature: 0x504E43, id: 2), GetApplicationEventTarget(), 0, &r2)
        carbonRefs = [r1, r2]
        logLine("OK Carbon hotkeys registered")
    }

    func checkPanicFile() {
        let f = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".sina/PANIC.now")
        if FileManager.default.fileExists(atPath: f.path) {
            try? FileManager.default.removeItem(at: f)
            firePanic("panic-file")
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
