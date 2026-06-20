import Cocoa
import WebKit

final class HeartLauncher {
    static let port = ProcessInfo.processInfo.environment["APPLE_HEALTH_PORT"] ?? "13025"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        let resources = Bundle.main.bundlePath + "/Contents/Resources/apple-health-bundle"
        return resources
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("apple-health-app-launch.log")
        let line = "\(ISO8601DateFormatter().string(from: Date())) \(msg)\n"
        if let data = line.data(using: .utf8) {
            if FileManager.default.fileExists(atPath: log.path) {
                if let h = try? FileHandle(forWritingTo: log) {
                    h.seekToEndOfFile()
                    h.write(data)
                    try? h.close()
                }
            } else {
                try? data.write(to: log)
            }
        }
    }

    static func pythonPath() -> String {
        let candidates = [
            "/usr/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
            "/opt/homebrew/bin/python3",
        ]
        for p in candidates where FileManager.default.isExecutableFile(atPath: p) {
            return p
        }
        return "/usr/bin/python3"
    }

    static func healthOK(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/health") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            let ok = (resp as? HTTPURLResponse)?.statusCode == 200
            completion(ok)
        }.resume()
    }

    static func startServer(completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                logLine("server already healthy")
                completion(true)
                return
            }
            let script = bundleRoot() + "/scripts/apple-health-server.py"
            guard FileManager.default.fileExists(atPath: script) else {
                logLine("FAIL missing server script \(script)")
                completion(false)
                return
            }
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: pythonPath())
            proc.arguments = [script]
            var env = ProcessInfo.processInfo.environment
            env["APPLE_HEALTH_BUNDLE_ROOT"] = bundleRoot()
            env["APPLE_HEALTH_STANDALONE"] = "1"
            env["APPLE_HEALTH_PORT"] = port
            let home = FileManager.default.homeDirectoryForCurrentUser
            let sourceA = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
            if FileManager.default.fileExists(atPath: sourceA.path) {
                env["SINA_SOURCE_A"] = sourceA.path
            }
            env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
            proc.environment = env
            let log = home.appendingPathComponent(".sina/apple-health-server.log")
            try? FileManager.default.createDirectory(at: home.appendingPathComponent(".sina"), withIntermediateDirectories: true)
            if FileManager.default.fileExists(atPath: log.path) {
                try? "".write(to: log, atomically: true, encoding: .utf8)
            }
            if let h = try? FileHandle(forWritingTo: log) {
                proc.standardOutput = h
                proc.standardError = h
            }
            do {
                try proc.run()
                serverProcess = proc
                let pidFile = home.appendingPathComponent(".sina/apple-health-server.pid")
                try? "\(proc.processIdentifier)".write(to: pidFile, atomically: true, encoding: .utf8)
                logLine("started server pid=\(proc.processIdentifier)")
                waitForHealth(attempts: 0, completion: completion)
            } catch {
                logLine("FAIL start server \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    static func waitForHealth(attempts: Int, completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                completion(true)
            } else if attempts < 48 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForHealth(attempts: attempts + 1, completion: completion)
                }
            } else {
                logLine("FAIL server timeout")
                completion(false)
            }
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    let port = HeartLauncher.port

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        HeartLauncher.logLine("double-click launch")
        let config = WKWebViewConfiguration()
        webView = WKWebView(frame: .zero, configuration: config)
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 960, height: 720),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Apple Health"
        window.contentView = webView
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        showLoading()
        HeartLauncher.startServer { ok in
            DispatchQueue.main.async {
                if ok {
                    self.pollHealthAndLoad(attempts: 0)
                } else {
                    self.showFailure()
                }
            }
        }
    }

    func showLoading() {
        let html = """
        <html><body style='background:#0c1018;color:#e8ecf4;font-family:system-ui;padding:40px;text-align:center'>
        <h1>Apple Health</h1>
        <p>Starting wellness heart…</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func showFailure() {
        let alert = NSAlert()
        alert.messageText = "Apple Health"
        alert.informativeText = "Could not start the server. Log: ~/.sina/apple-health-server.log"
        alert.alertStyle = .warning
        alert.runModal()
        let html = """
        <html><body style='background:#0c1018;color:#e8ecf4;font-family:system-ui;padding:40px'>
        <h1>Apple Health</h1>
        <p>Server failed to start. Double-click again or check ~/.sina/apple-health-server.log</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func pollHealthAndLoad(attempts: Int) {
        guard let healthURL = URL(string: "http://127.0.0.1:\(port)/health") else { return }
        URLSession.shared.dataTask(with: healthURL) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200,
                   let pageURL = URL(string: "http://127.0.0.1:\(self.port)/") {
                    HeartLauncher.logLine("window loading UI")
                    self.webView.load(URLRequest(url: pageURL))
                } else if attempts < 48 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                        self.pollHealthAndLoad(attempts: attempts + 1)
                    }
                } else {
                    self.showFailure()
                }
            }
        }.resume()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
