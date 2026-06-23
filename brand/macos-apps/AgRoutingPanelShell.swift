import Cocoa
import WebKit

final class AgLauncher {
    static let port = ProcessInfo.processInfo.environment["AG_ROUTING_PANEL_PORT"] ?? "8782"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/ag-routing-panel-bundle"
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("ag-routing-panel-app-launch.log")
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
        for p in ["/usr/bin/python3", "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3", "/opt/homebrew/bin/python3"]
            where FileManager.default.isExecutableFile(atPath: p) { return p }
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
            let script = bundleRoot() + "/scripts/ag-routing-panel-server.py"
            guard FileManager.default.fileExists(atPath: script) else {
                logLine("FAIL missing server script")
                completion(false)
                return
            }
            let home = FileManager.default.homeDirectoryForCurrentUser
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: pythonPath())
            proc.arguments = [script]
            var env = ProcessInfo.processInfo.environment
            env["AG_ROUTING_PANEL_BUNDLE_ROOT"] = bundleRoot()
            env["AG_ROUTING_PANEL_PORT"] = port
            let sourceA = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
            if FileManager.default.fileExists(atPath: sourceA.path) {
                env["SINA_SOURCE_A"] = sourceA.path
            }
            env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
            proc.environment = env
            do {
                try proc.run()
                serverProcess = proc
                waitForHealth(attempts: 0, completion: completion)
            } catch {
                logLine("FAIL start \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    static func waitForHealth(attempts: Int, completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok { completion(true) }
            else if attempts < 40 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForHealth(attempts: attempts + 1, completion: completion)
                }
            } else {
                completion(false)
            }
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    let port = AgLauncher.port
    let appRouter = SinaAppRouter(homeApp: .agRouting)

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "AG Routing Panel")
        AgLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1180, height: 820),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "AG Routing Panel"
        window.isReleasedWhenClosed = false
        SinaStandaloneShell.showWindow(window)
        let config = WKWebViewConfiguration()
        appRouter.prepare(config: config)
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        appRouter.attach(to: webView)
        window.contentView = webView
        showLoading()
        AgLauncher.startServer { ok in
            DispatchQueue.main.async {
                ok ? self.loadUI(attempts: 0) : self.showFailure()
            }
        }
    }

    func showLoading() {
        webView.loadHTMLString(
            "<html><body style='background:#0a0e14;color:#e8eef4;font-family:system-ui;padding:48px;text-align:center'><h1>AG Routing Panel</h1><p style='color:#8b9cb3'>Agent light routing · starting…</p></body></html>",
            baseURL: nil
        )
    }

    func showFailure() {
        webView.loadHTMLString(
            "<html><body style='background:#0a0e14;color:#e8eef4;padding:40px'><h1>AG Routing Panel</h1><p>Server failed — log ~/.sina/ag-routing-panel-app-launch.log</p></body></html>",
            baseURL: nil
        )
    }

    func loadUI(attempts: Int) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/") else { return }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200 {
                    self.webView.load(URLRequest(url: url))
                } else if attempts < 40 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { self.loadUI(attempts: attempts + 1) }
                } else {
                    self.showFailure()
                }
            }
        }.resume()
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        SinaStandaloneShell.handleReopen(window: window)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }

    func applicationWillTerminate(_ notification: Notification) {
        if let proc = AgLauncher.serverProcess, proc.isRunning { proc.terminate() }
    }
}

@main
struct AgRoutingPanelAppMain {
    static func main() {
        guard SinaStandaloneShell.prepareApp(bundleId: "com.sina.agrouting.standalone") else { return }
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.run()
    }
}
