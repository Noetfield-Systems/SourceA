import Cocoa
import WebKit

final class HeartLauncher {
    static let port = ProcessInfo.processInfo.environment["CHAT_UNIFY_PORT"] ?? "13023"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/chat-unify-bundle"
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("chat-unify-app-launch.log")
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
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func formWireOK(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/form/") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func recycleStalePort(completion: @escaping () -> Void) {
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/bash")
        task.arguments = ["-c", "lsof -ti:\(port) | xargs kill -9 2>/dev/null || true; sleep 0.35"]
        task.terminationHandler = { _ in completion() }
        do {
            try task.run()
        } catch {
            completion()
        }
    }

    static func launchServerProcess(completion: @escaping (Bool) -> Void) {
        let script = bundleRoot() + "/scripts/chat-unify-server.py"
        guard FileManager.default.fileExists(atPath: script) else {
            logLine("FAIL missing server script \(script)")
            completion(false)
            return
        }
        let home = FileManager.default.homeDirectoryForCurrentUser
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: pythonPath())
        proc.arguments = [script]
        var env = ProcessInfo.processInfo.environment
        env["CHAT_UNIFY_BUNDLE_ROOT"] = bundleRoot()
        env["CHAT_UNIFY_STANDALONE"] = "1"
        env["CHAT_UNIFY_PORT"] = port
        let sourceA = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
        if FileManager.default.fileExists(atPath: sourceA.path) {
            env["SINA_SOURCE_A"] = sourceA.path
        }
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        proc.environment = env
        do {
            try proc.run()
            serverProcess = proc
            let pidFile = home.appendingPathComponent(".sina/chat-unify-server.pid")
            try? "\(proc.processIdentifier)".write(to: pidFile, atomically: true, encoding: .utf8)
            logLine("started server pid=\(proc.processIdentifier)")
            waitForHealth(attempts: 0, completion: completion)
        } catch {
            logLine("FAIL start server \(error.localizedDescription)")
            completion(false)
        }
    }

    static func startServer(completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                formWireOK { wired in
                    if wired {
                        logLine("server already healthy + form wired")
                        completion(true)
                    } else {
                        logLine("stale server on :\(port) — recycling for form wire")
                        recycleStalePort {
                            launchServerProcess(completion: completion)
                        }
                    }
                }
                return
            }
            launchServerProcess(completion: completion)
        }
    }

    static func waitForHealth(attempts: Int, completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                formWireOK { wired in
                    completion(wired)
                }
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
    let appRouter = SinaAppRouter(homeApp: .chat)

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "Chat Unify")
        HeartLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1100, height: 780),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Chat Unify"
        window.isReleasedWhenClosed = false
        SinaStandaloneShell.showWindow(window)
        let config = WKWebViewConfiguration()
        appRouter.prepare(config: config)
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        appRouter.attach(to: webView)
        window.contentView = webView
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
        <html><body style='background:#08060e;color:#f5f3ff;font-family:system-ui;padding:48px;text-align:center'>
        <div style='font-size:2.5rem;margin-bottom:16px'>⇄</div>
        <h1 style='font-weight:600'>Chat Unify</h1>
        <p style='color:#9b94ad'>Starting local merge engine…</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func showFailure() {
        let alert = NSAlert()
        alert.messageText = "Chat Unify"
        alert.informativeText = "Could not start the server. Log: ~/.sina/chat-unify-server.log"
        alert.alertStyle = .warning
        alert.runModal()
        let html = """
        <html><body style='background:#08060e;color:#f5f3ff;font-family:system-ui;padding:40px'>
        <h1>Chat Unify</h1>
        <p>Server failed to start. Double-click again or check ~/.sina/chat-unify-server.log</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func pollHealthAndLoad(attempts: Int) {
        guard let healthURL = URL(string: "http://127.0.0.1:\(port)/health") else { return }
        URLSession.shared.dataTask(with: healthURL) { data, resp, _ in
            DispatchQueue.main.async {
                guard let http = resp as? HTTPURLResponse, http.statusCode == 200 else {
                    if attempts < 48 {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                            self.pollHealthAndLoad(attempts: attempts + 1)
                        }
                    } else {
                        self.showFailure()
                    }
                    return
                }
                var uiVer = "4.2.0"
                if let data = data,
                   let row = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let v = row["ui_version"] as? String, !v.isEmpty {
                    uiVer = v
                }
                if let pageURL = URL(string: "http://127.0.0.1:\(self.port)/?ui=\(uiVer)&t=\(Int(Date().timeIntervalSince1970))") {
                    HeartLauncher.logLine("window loading UI \(uiVer)")
                    self.webView.load(URLRequest(url: pageURL))
                }
            }
        }.resume()
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        SinaStandaloneShell.handleReopen(window: window)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    func applicationWillTerminate(_ notification: Notification) {
        if let proc = HeartLauncher.serverProcess, proc.isRunning {
            proc.terminate()
        }
    }
}

@main
struct ChatUnifyAppMain {
    static func main() {
        guard SinaStandaloneShell.prepareApp(bundleId: "com.sina.chatunify.standalone") else { return }
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}
