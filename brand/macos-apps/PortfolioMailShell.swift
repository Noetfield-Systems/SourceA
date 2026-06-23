import Cocoa
import WebKit

final class StackLauncher {
    static let hubPort = ProcessInfo.processInfo.environment["SINA_COMMAND_PORT"] ?? "13020"
    static var bootProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/portfolio-mail-bundle"
    }

    static func sourceA() -> URL {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let desktop = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
        if FileManager.default.fileExists(atPath: desktop.path) {
            return desktop
        }
        return home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("portfolio-mail-app-launch.log")
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

    static func healthOK(port: String, path: String = "/health", completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(port)\(path)") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func mailHubReady(completion: @escaping (Bool) -> Void) {
        healthOK(port: hubPort, path: "/health") { hubUp in
            completion(hubUp)
        }
    }

    static func bootScriptPath() -> String {
        let bundled = bundleRoot() + "/scripts/portfolio-mail-stack-boot.sh"
        if FileManager.default.fileExists(atPath: bundled) {
            return bundled
        }
        return sourceA().appendingPathComponent("scripts/portfolio-mail-stack-boot.sh").path
    }

    static func startStack(completion: @escaping (Bool) -> Void) {
        mailHubReady { ready in
            if ready {
                logLine("stack already ready")
                completion(true)
                return
            }
            let script = bootScriptPath()
            guard FileManager.default.fileExists(atPath: script) else {
                logLine("FAIL missing boot script \(script)")
                completion(false)
                return
            }
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: "/bin/bash")
            proc.arguments = [script]
            var env = ProcessInfo.processInfo.environment
            env["SINA_SOURCE_A"] = sourceA().path
            env["SINA_COMMAND_PORT"] = hubPort
            env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
            proc.environment = env
            do {
                try proc.run()
                bootProcess = proc
                logLine("boot pid=\(proc.processIdentifier)")
                proc.terminationHandler = { _ in
                    waitForReady(attempts: 0, completion: completion)
                }
            } catch {
                logLine("FAIL boot \(error.localizedDescription)")
                completion(false)
            }
        }
    }

    static func waitForReady(attempts: Int, completion: @escaping (Bool) -> Void) {
        mailHubReady { ok in
            if ok {
                completion(true)
            } else if attempts < 60 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForReady(attempts: attempts + 1, completion: completion)
                }
            } else {
                logLine("FAIL stack timeout")
                completion(false)
            }
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    let hubPort = StackLauncher.hubPort
    let appRouter = SinaAppRouter(homeApp: .mail)

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "Portfolio Mail")
        StackLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1200, height: 820),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Portfolio Mail"
        window.isReleasedWhenClosed = false
        SinaStandaloneShell.showWindow(window)
        let config = WKWebViewConfiguration()
        appRouter.prepare(config: config)
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        appRouter.attach(to: webView)
        window.contentView = webView
        showLoading()
        StackLauncher.startStack { ok in
            DispatchQueue.main.async {
                if ok {
                    self.loadMailHub(attempts: 0)
                } else {
                    self.showFailure()
                }
            }
        }
    }

    func showLoading() {
        let html = """
        <html><body style='background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:48px;text-align:center'>
        <div style='font-size:2.5rem;margin-bottom:16px'>✉</div>
        <h1 style='font-weight:600'>Portfolio Mail</h1>
        <p style='color:#94a3b8'>Wiring Hub · Chat Unify · N8N Integration…</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func showFailure() {
        let alert = NSAlert()
        alert.messageText = "Portfolio Mail"
        alert.informativeText = "Could not start the mail stack. Log: ~/.sina/portfolio-mail-app-launch.log"
        alert.alertStyle = .warning
        alert.runModal()
        let html = """
        <html><body style='background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:40px'>
        <h1>Portfolio Mail</h1>
        <p>Stack failed to start. Double-click again or check ~/.sina/portfolio-mail-stack-boot.log</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func loadMailHub(attempts: Int) {
        guard let pageURL = URL(string: "http://127.0.0.1:\(hubPort)/mail-hub/?t=\(Int(Date().timeIntervalSince1970))") else { return }
        URLSession.shared.dataTask(with: pageURL) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200 {
                    StackLauncher.logLine("window loading mail-hub")
                    self.webView.load(URLRequest(url: pageURL))
                } else if attempts < 48 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                        self.loadMailHub(attempts: attempts + 1)
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
}

@main
struct PortfolioMailAppMain {
    static func main() {
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}
