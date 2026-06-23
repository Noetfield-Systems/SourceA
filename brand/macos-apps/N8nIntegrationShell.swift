import Cocoa
import WebKit

final class HeartLauncher {
    static let port = ProcessInfo.processInfo.environment["N8N_INTEGRATION_PORT"] ?? "13026"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/n8n-integration-bundle"
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("n8n-integration-app-launch.log")
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

    static func startServer(completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                logLine("server already healthy")
                completion(true)
                return
            }
            let script = bundleRoot() + "/scripts/n8n-integration-server.py"
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
            env["N8N_INTEGRATION_BUNDLE_ROOT"] = bundleRoot()
            env["N8N_INTEGRATION_STANDALONE"] = "1"
            env["N8N_INTEGRATION_PORT"] = port
            let sourceA = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
            if FileManager.default.fileExists(atPath: sourceA.path) {
                env["SINA_SOURCE_A"] = sourceA.path
            }
            env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
            proc.environment = env
            do {
                try proc.run()
                serverProcess = proc
                let pidFile = home.appendingPathComponent(".sina/n8n-integration-server.pid")
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
    let appRouter = SinaAppRouter(homeApp: .n8n)

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "N8N Integration")
        HeartLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1100, height: 780),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "N8N Integration"
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
        <html><body style='background:#0a0806;color:#fff8f2;font-family:system-ui;padding:48px;text-align:center'>
        <div style='font-size:2.5rem;margin-bottom:16px'>⎇</div>
        <h1 style='font-weight:600'>N8N Integration</h1>
        <p style='color:#a89a8c'>Starting automation spine…</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func showFailure() {
        let alert = NSAlert()
        alert.messageText = "N8N Integration"
        alert.informativeText = "Could not start the server. Log: ~/.sina/n8n-integration-boot.log"
        alert.alertStyle = .warning
        alert.runModal()
        let html = """
        <html><body style='background:#0a0806;color:#fff8f2;font-family:system-ui;padding:40px'>
        <h1>N8N Integration</h1>
        <p>Server failed to start. Double-click again or check ~/.sina/n8n-integration-boot.log</p>
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
struct N8nIntegrationAppMain {
    static func main() {
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}
