import AppKit
import Foundation

// Double-click Desktop app — REAL stop: pause launchd, kill agents, show honest receipt.

func logLine(_ msg: String) {
    let home = FileManager.default.homeDirectoryForCurrentUser
    let log = home.appendingPathComponent(".sina/mac-health-panic-hotkey.log")
    let line = "\(ISO8601DateFormatter().string(from: Date())) [stop-app] \(msg)\n"
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

func pythonPath() -> String {
    for p in [
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        "/opt/homebrew/bin/python3",
        "/usr/bin/python3",
    ] where FileManager.default.isExecutableFile(atPath: p) {
        return p
    }
    return "/usr/bin/python3"
}

struct StopResult {
    let proof: String
    let killCount: Int
    let ok: Bool
}

func runEmergencyStop() -> StopResult {
    logLine("desktop double-click START")
    let quietFlag = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent(".sina/mac-health-quiet-v1.flag")
    if !FileManager.default.fileExists(atPath: quietFlag.path),
       FileManager.default.fileExists(atPath: "/System/Library/Sounds/Basso.aiff") {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/afplay")
        p.arguments = ["/System/Library/Sounds/Basso.aiff"]
        try? p.run()
    }

    let root = sourceAPath()
    let script = root + "/scripts/mac_health_emergency_stop_v1.py"
    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: pythonPath())
    proc.arguments = [script, "--trigger", "desktop-stop", "--json"]
    var env = ProcessInfo.processInfo.environment
    env["SINA_SOURCEA"] = root
    env["PYTHONPATH"] = root + "/scripts"
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    proc.environment = env
    let pipe = Pipe()
    proc.standardOutput = pipe
    proc.standardError = pipe
    do {
        try proc.run()
        proc.waitUntilExit()
    } catch {
        logLine("FAIL \(error.localizedDescription)")
        return StopResult(proof: "STOP failed: \(error.localizedDescription)", killCount: 0, ok: false)
    }
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    let raw = String(data: data, encoding: .utf8) ?? ""
    logLine("done exit=\(proc.terminationStatus) out=\(raw.prefix(300))")

    guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
        return StopResult(proof: raw.isEmpty ? "No output from stop script." : raw, killCount: 0, ok: false)
    }

    var lines: [String] = []
    if let proof = json["proof_lines"] as? [String], !proof.isEmpty {
        lines = proof
    } else if let founder = json["founder_line"] as? String {
        lines = [founder]
    } else {
        lines = [(json["summary"] as? String) ?? "Done"]
    }

    let killCount = (json["kill_count"] as? Int)
        ?? (json["kills"] as? [[String: Any]])?.count
        ?? 0

    if killCount == 0 {
        lines.insert(
            "Paused factory — 0 background kills. Cursor, Terminal, Claude still running.",
            at: 0
        )
        lines.append("For IDE lag: Mac Health → Cool Down → Restart Cursor.")
    } else {
        lines.insert("Killed \(killCount) background process(es). Landing tunnel kept alive.", at: 0)
    }

    let still = (json["still_running"] as? [[String: Any]]) ?? []
    if killCount == 0 && !still.isEmpty {
        let top = still.prefix(3).compactMap { row -> String? in
            let comm = (row["comm"] as? String) ?? "?"
            let cpu = (row["cpu_pct"] as? Double) ?? 0
            return "\(comm.prefix(20)) \(Int(cpu))%"
        }.joined(separator: " · ")
        if !top.isEmpty {
            lines.append("Still heavy: \(top)")
        }
    }

    return StopResult(
        proof: lines.joined(separator: "\n"),
        killCount: killCount,
        ok: (json["ok"] as? Bool) != false
    )
}

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
        DispatchQueue.global(qos: .userInitiated).async {
            let result = runEmergencyStop()
            DispatchQueue.main.async {
                let alert = NSAlert()
                if result.killCount > 0 {
                    alert.messageText = "⛔ STOPPED — \(result.killCount) killed"
                } else {
                    alert.messageText = "⛔ Paused — 0 kills (Cursor still open)"
                }
                alert.informativeText = result.proof
                alert.alertStyle = result.ok && result.killCount > 0 ? .informational : .warning
                alert.addButton(withTitle: "OK")
                alert.runModal()
                NSApp.terminate(nil)
            }
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
