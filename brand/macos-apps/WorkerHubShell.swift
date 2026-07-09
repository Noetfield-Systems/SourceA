import Cocoa
import WebKit

final class HubLauncher {
    static let hubPort = ProcessInfo.processInfo.environment["SINA_COMMAND_PORT"] ?? "13020"
    static var bootProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/worker-hub-bundle"
    }

    static func sourceA() -> URL? {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let candidates = [
            home.appendingPathComponent("Desktop/Noetfield-Systems/SourceA", isDirectory: true),
            home.appendingPathComponent("Desktop/SourceA", isDirectory: true),
        ]
        for c in candidates {
            let marker = c.appendingPathComponent("scripts/sina-command-server.py")
            if FileManager.default.fileExists(atPath: marker.path) { return c }
        }
        return nil
    }

    static func sourceALegacy() -> URL {
        FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Desktop/SourceA", isDirectory: true)
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("worker-hub-app-launch.log")
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

    static func hubReady(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(hubPort)/health") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func bootScriptPath() -> String {
        let bundled = bundleRoot() + "/scripts/worker-hub-stack-boot.sh"
        if FileManager.default.fileExists(atPath: bundled) { return bundled }
        if let sa = sourceA() {
            return sa.appendingPathComponent("scripts/worker-hub-stack-boot.sh").path
        }
        return sourceALegacy().appendingPathComponent("scripts/worker-hub-stack-boot.sh").path
    }

    static func startStack(completion: @escaping (Bool) -> Void) {
        hubReady { ready in
            if ready {
                logLine("hub already ready")
                completion(true)
                return
            }
            let script = bootScriptPath()
            guard FileManager.default.fileExists(atPath: script) else {
                logLine("FAIL missing boot script")
                completion(false)
                return
            }
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: "/bin/bash")
            proc.arguments = [script]
            var env = ProcessInfo.processInfo.environment
            if let sa = sourceA() {
                env["SINA_SOURCE_A"] = sa.path
            }
            env["SINA_COMMAND_PORT"] = hubPort
            proc.environment = env
            do {
                try proc.run()
                bootProcess = proc
                proc.terminationHandler = { _ in waitForReady(attempts: 0, completion: completion) }
            } catch {
                logLine("FAIL boot \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    static func waitForReady(attempts: Int, completion: @escaping (Bool) -> Void) {
        hubReady { ok in
            if ok { completion(true) }
            else if attempts < 60 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForReady(attempts: attempts + 1, completion: completion)
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
    let hubPort = HubLauncher.hubPort
    let appRouter = SinaAppRouter(homeApp: .hub)

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "Worker Hub")
        HubLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1200, height: 820),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Worker Hub"
        window.isReleasedWhenClosed = false
        SinaStandaloneShell.showWindow(window)
        let config = WKWebViewConfiguration()
        appRouter.prepare(config: config)
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        appRouter.attach(to: webView)
        window.contentView = webView
        showLoading()
        HubLauncher.startStack { ok in
            DispatchQueue.main.async {
                ok ? self.loadHub(attempts: 0) : self.showFailure()
            }
        }
    }

    func showLoading() {
        webView.loadHTMLString("""
        <html><body style='background:#f6f8fc;color:#1a2332;font-family:system-ui;padding:48px;text-align:center'>
        <div style='font-size:2.5rem;margin-bottom:16px'>⚡</div>
        <h1>Worker Hub</h1>
        <p style='color:#5c6b7f'>Starting stack · wiring apps…</p>
        </body></html>
        """, baseURL: nil)
    }

    func showFailure() {
        webView.loadHTMLString("""
        <html><body style='background:#f6f8fc;font-family:system-ui;padding:40px'>
        <h1>Worker Hub</h1>
        <p>Stack failed — see ~/.sina/worker-hub-app-launch.log</p>
        </body></html>
        """, baseURL: nil)
    }

    func loadHub(attempts: Int) {
        guard let url = URL(string: "http://127.0.0.1:\(hubPort)/?t=\(Int(Date().timeIntervalSince1970))") else { return }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200 {
                    self.webView.load(URLRequest(url: url))
                } else if attempts < 48 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { self.loadHub(attempts: attempts + 1) }
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
}

@main
struct WorkerHubAppMain {
    static func main() {
        guard SinaStandaloneShell.prepareApp(bundleId: "com.sina.workerhub.standalone") else { return }
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.run()
    }
}
