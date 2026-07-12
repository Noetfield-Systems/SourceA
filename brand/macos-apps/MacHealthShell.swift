import Cocoa
import WebKit

final class HeartLauncher {
    static let port = ProcessInfo.processInfo.environment["MAC_HEALTH_PORT"] ?? "13024"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/mac-health-bundle"
    }

    static func sourceAPath() -> String {
        if let env = ProcessInfo.processInfo.environment["SINA_SOURCEA"], !env.isEmpty {
            let script = env + "/scripts/mac-health-guard-server.py"
            if FileManager.default.fileExists(atPath: script) { return env }
        }
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        let candidates = [
            home + "/Desktop/Noetfield-Systems/SourceA",
            home + "/Desktop/SourceA",
        ]
        for base in candidates {
            let script = base + "/scripts/mac-health-guard-server.py"
            if FileManager.default.fileExists(atPath: script) { return base }
        }
        return bundleRoot().replacingOccurrences(of: "/Contents/Resources/mac-health-bundle", with: "")
    }

    static func serverScriptPath() -> String {
        let sa = sourceAPath()
        return sa + "/scripts/mac-health-guard-server.py"
    }

    static func logLine(_ msg: String) {
        let log = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".sina/mac-health-app-launch.log")
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

    static func pythonPath() -> String {
        for p in [
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
        ] where FileManager.default.isExecutableFile(atPath: p) {
            return p
        }
        return "/usr/bin/python3"
    }

    static func pythonEnv() -> [String: String] {
        var env = ProcessInfo.processInfo.environment
        let sa = sourceAPath()
        env["SINA_SOURCEA"] = sa
        env["PYTHONPATH"] = sa + "/scripts"
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        return env
    }

    static func healthOK(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/health") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func startServer(completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                logLine("server already healthy")
                completion(true)
                return
            }
            let script = serverScriptPath()
            guard FileManager.default.fileExists(atPath: script) else {
                logLine("FAIL missing server script")
                completion(false)
                return
            }
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: pythonPath())
            proc.arguments = [script]
            var env = pythonEnv()
            if !FileManager.default.fileExists(atPath: sourceAPath() + "/scripts/mac-health-guard-server.py") {
                env["MAC_HEALTH_BUNDLE_ROOT"] = bundleRoot()
            }
            env["MAC_HEALTH_STANDALONE"] = "1"
            env["MAC_HEALTH_PORT"] = port
            proc.environment = env
            let log = FileManager.default.homeDirectoryForCurrentUser
                .appendingPathComponent(".sina/mac-health-guard-server.log")
            if let h = try? FileHandle(forWritingTo: log) {
                proc.standardOutput = h
                proc.standardError = h
            }
            do {
                try proc.run()
                serverProcess = proc
                waitForHealth(attempts: 0, completion: completion)
            } catch {
                logLine("FAIL start server \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    static func waitForHealth(attempts: Int, completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok { completion(true) }
            else if attempts < 48 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForHealth(attempts: attempts + 1, completion: completion)
                }
            } else { completion(false) }
        }
    }
}

/// Native actions — web buttons cannot restart Cursor from inside Cursor; Swift can spawn detached work.
enum NativeActions {
    static func runPythonSync(args: [String], timeout: TimeInterval = 120) -> String {
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: HeartLauncher.pythonPath())
        proc.arguments = args
        proc.environment = HeartLauncher.pythonEnv()
        let pipe = Pipe()
        proc.standardOutput = pipe
        proc.standardError = pipe
        do {
            var output = Data()
            let outputLock = NSLock()
            pipe.fileHandleForReading.readabilityHandler = { handle in
                let chunk = handle.availableData
                if !chunk.isEmpty {
                    outputLock.lock()
                    output.append(chunk)
                    outputLock.unlock()
                }
            }
            try proc.run()
            let group = DispatchGroup()
            group.enter()
            DispatchQueue.global().async {
                proc.waitUntilExit()
                group.leave()
            }
            _ = group.wait(timeout: .now() + timeout)
            pipe.fileHandleForReading.readabilityHandler = nil
            outputLock.lock()
            let data = output
            outputLock.unlock()
            return String(data: data, encoding: .utf8) ?? ""
        } catch {
            return "Error: \(error.localizedDescription)"
        }
    }

    static func runPythonDetached(code: String) {
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: HeartLauncher.pythonPath())
        proc.arguments = ["-c", code]
        proc.environment = HeartLauncher.pythonEnv()
        try? proc.run()
    }

    static func openDesktopStopApp() {
        let desktop = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Desktop/⛔ STOP AGENTS.app")
        if FileManager.default.fileExists(atPath: desktop.path) {
            NSWorkspace.shared.openApplication(at: desktop, configuration: NSWorkspace.OpenConfiguration()) { _, _ in }
        } else {
            let alert = NSAlert()
            alert.messageText = "Open ⛔ STOP AGENTS on Desktop"
            alert.informativeText = "That app restarts Cursor and kills agents — works outside this window."
            alert.runModal()
        }
    }

    static func handle(_ action: String, completion: @escaping (String) -> Void) {
        DispatchQueue.global(qos: .userInitiated).async {
            let sa = HeartLauncher.sourceAPath()
            var result = ""
            switch action {
            case "restart_cursor", "cpu_restart_cursor":
                HeartLauncher.logLine("native restart_cursor detached")
                runPythonDetached(code: """
import time; time.sleep(0.3)
from mac_health_cpu_relief_v1 import restart_cursor
restart_cursor()
""")
                result = "Restarting Cursor now — window will close and reopen in ~5 seconds."
            case "emergency_stop", "stop_agents":
                let script = sa + "/scripts/mac_health_emergency_stop_v1.py"
                let out = runPythonSync(args: [script, "--trigger", "ui", "--fast", "--json"])
                if let data = out.data(using: .utf8),
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                    result = (json["founder_line"] as? String) ?? (json["summary"] as? String) ?? out
                } else { result = out.isEmpty ? "Agents stopped." : out }
                result += "\n\nStill laggy? Double-click ⛔ STOP AGENTS on Desktop (restarts Cursor)."
            case "desktop_stop":
                openDesktopStopApp()
                result = "Opening Desktop STOP app…"
            default:
                let py = """
import json
from mac_health_guard import handle_action
print(json.dumps(handle_action({"action": "\(action)", "standalone": True})))
"""
                let out = runPythonSync(args: ["-c", py])
                result = out.isEmpty ? "Done." : String(out.prefix(800))
            }
            DispatchQueue.main.async { completion(result) }
        }
    }
}

class NativeBridge: NSObject, WKScriptMessageHandler {
    weak var webView: WKWebView?

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "mhgNative", let action = message.body as? String else { return }
        HeartLauncher.logLine("native action \(action)")
        NativeActions.handle(action) { result in
            let safe = result.replacingOccurrences(of: "\\", with: "\\\\")
                .replacingOccurrences(of: "'", with: "\\'")
                .replacingOccurrences(of: "\n", with: "\\n")
            self.webView?.evaluateJavaScript("window.__mhgNativeDone('\(safe)')", completionHandler: nil)
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var nativeBridge: NativeBridge!
    let port = HeartLauncher.port

    func setupMenu() {
        let main = NSMenu()
        let appItem = NSMenuItem()
        main.addItem(appItem)
        let appMenu = NSMenu()
        appItem.submenu = appMenu
        appMenu.addItem(NSMenuItem(title: "⛔ Stop agents (native)", action: #selector(menuStop(_:)), keyEquivalent: ""))
        appMenu.addItem(NSMenuItem(title: "↻ Restart Cursor (native)", action: #selector(menuRestart(_:)), keyEquivalent: ""))
        appMenu.addItem(NSMenuItem(title: "Open Desktop ⛔ STOP AGENTS", action: #selector(menuDesktopStop(_:)), keyEquivalent: ""))
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        NSApp.mainMenu = main
    }

    @objc func menuStop(_ sender: Any?) {
        NativeActions.handle("emergency_stop") { msg in
            let a = NSAlert()
            a.messageText = "⛔ Stop agents"
            a.informativeText = msg
            a.runModal()
        }
    }

    @objc func menuRestart(_ sender: Any?) {
        let a = NSAlert()
        a.messageText = "Restart Cursor?"
        a.informativeText = "Save files first. Cursor closes and reopens in ~5 seconds."
        a.addButton(withTitle: "Restart")
        a.addButton(withTitle: "Cancel")
        if a.runModal() == .alertFirstButtonReturn {
            NativeActions.handle("restart_cursor") { _ in }
        }
    }

    @objc func menuDesktopStop(_ sender: Any?) { NativeActions.openDesktopStopApp() }

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        setupMenu()
        HeartLauncher.logLine("double-click launch")

        nativeBridge = NativeBridge()
        let config = WKWebViewConfiguration()
        config.userContentController.add(nativeBridge, name: "mhgNative")
        webView = WKWebView(frame: .zero, configuration: config)
        nativeBridge.webView = webView

        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 960, height: 720),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Mac Health Guard"
        window.contentView = webView
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        showLoading()
        HeartLauncher.startServer { ok in
            DispatchQueue.main.async {
                ok ? self.pollHealthAndLoad(attempts: 0) : self.showFailure()
            }
        }
    }

    func showLoading() {
        webView.loadHTMLString("<html><body style='background:#0f1923;color:#eee;font-family:system-ui;padding:40px;text-align:center'><h1>Mac Health Guard</h1><p>Starting…</p></body></html>", baseURL: nil)
    }

    func showFailure() {
        NSAlert().runModal()
        webView.loadHTMLString("<html><body style='background:#0f1923;color:#eee;padding:40px'><h1>Heart failed</h1><p>See ~/.sina/mac-health-guard-server.log</p></body></html>", baseURL: nil)
    }

    func pollHealthAndLoad(attempts: Int) {
        guard let healthURL = URL(string: "http://127.0.0.1:\(port)/health") else { return }
        URLSession.shared.dataTask(with: healthURL) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200,
                   let pageURL = URL(string: "http://127.0.0.1:\(self.port)/?native=1") {
                    HeartLauncher.logLine("window loading UI")
                    self.webView.load(URLRequest(url: pageURL))
                } else if attempts < 48 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { self.pollHealthAndLoad(attempts: attempts + 1) }
                } else { self.showFailure() }
            }
        }.resume()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
