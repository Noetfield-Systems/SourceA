import Cocoa
import WebKit

final class ForgeWebView: WKWebView {
    override var acceptsFirstResponder: Bool { true }

    override func performKeyEquivalent(with event: NSEvent) -> Bool {
        guard event.modifierFlags.contains(.command),
              let key = event.charactersIgnoringModifiers?.lowercased() else {
            return super.performKeyEquivalent(with: event)
        }
        switch key {
        case "v":
            return NSApp.sendAction(#selector(NSText.paste(_:)), to: nil, from: self)
        case "c":
            return NSApp.sendAction(#selector(NSText.copy(_:)), to: nil, from: self)
        case "x":
            return NSApp.sendAction(#selector(NSText.cut(_:)), to: nil, from: self)
        case "a":
            return NSApp.sendAction(#selector(NSText.selectAll(_:)), to: nil, from: self)
        case "z":
            if event.modifierFlags.contains(.shift) {
                return NSApp.sendAction(Selector(("redo:")), to: nil, from: self)
            }
            return NSApp.sendAction(Selector(("undo:")), to: nil, from: self)
        default:
            return super.performKeyEquivalent(with: event)
        }
    }
}

final class HeartLauncher {
    static let port = ProcessInfo.processInfo.environment["FORGE_TERMINAL_PORT"] ?? "13029"
    static var serverProcess: Process?

    static func bundleRoot() -> String {
        Bundle.main.bundlePath + "/Contents/Resources/forge-terminal-bundle"
    }

    static func logLine(_ msg: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent(".sina", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let log = dir.appendingPathComponent("forge-terminal-app-launch.log")
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
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "/usr/bin/python3",
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

    static func terminalOK(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/terminal/index.html") else {
            completion(false)
            return
        }
        URLSession.shared.dataTask(with: url) { _, resp, _ in
            completion((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    static func recycleStalePort(completion: @escaping () -> Void) {
        let script = """
        PORT=\(port)
        for pid in $(lsof -ti:$PORT 2>/dev/null); do
          cmd=$(ps -p "$pid" -o command= 2>/dev/null || true)
          if echo "$cmd" | grep -q 'forge-terminal-server.py'; then
            kill -9 "$pid" 2>/dev/null || true
          fi
        done
        sleep 0.35
        """
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/bash")
        task.arguments = ["-c", script]
        task.terminationHandler = { _ in completion() }
        do {
            try task.run()
        } catch {
            completion()
        }
    }

    static func launchServerProcess(completion: @escaping (Bool) -> Void) {
        let script = bundleRoot() + "/scripts/forge-terminal-server.py"
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
        env["FORGE_TERMINAL_BUNDLE_ROOT"] = bundleRoot()
        env["FORGE_TERMINAL_STANDALONE"] = "1"
        env["FORGE_TERMINAL_PORT"] = port
        env["FORGE_TERMINAL_USE_LIVE_UI"] = "0"
        let sourceA = home.appendingPathComponent("Desktop/SourceA", isDirectory: true)
        if FileManager.default.fileExists(atPath: sourceA.path) {
            env["SINA_SOURCE_A"] = sourceA.path
        }
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        proc.environment = env
        do {
            try proc.run()
            serverProcess = proc
            let pidFile = home.appendingPathComponent(".sina/forge-terminal-server.pid")
            try? "\(proc.processIdentifier)".write(to: pidFile, atomically: true, encoding: .utf8)
            logLine("started server pid=\(proc.processIdentifier)")
            waitForReady(attempts: 0, completion: completion)
        } catch {
            logLine("FAIL start server \(error.localizedDescription)")
            completion(false)
        }
    }

    static func startServer(completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                terminalOK { wired in
                    if wired {
                        logLine("server already healthy + terminal wired")
                        completion(true)
                    } else {
                        logLine("stale server on :\(port) — recycling")
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

    static func waitForReady(attempts: Int, completion: @escaping (Bool) -> Void) {
        healthOK { ok in
            if ok {
                terminalOK { wired in
                    completion(wired)
                }
            } else if attempts < 48 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                    waitForReady(attempts: attempts + 1, completion: completion)
                }
            } else {
                logLine("FAIL server timeout")
                completion(false)
            }
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKScriptMessageHandler {
    var window: NSWindow!
    var webView: ForgeWebView!
    let port = HeartLauncher.port

    /// Safe JS string literal — avoids NSJSONSerialization crash on Swift String (H1).
    private func jsStringLiteral(_ value: String) -> String {
        var out = "\""
        for scalar in value.unicodeScalars {
            switch scalar {
            case "\\": out += "\\\\"
            case "\"": out += "\\\""
            case "\n": out += "\\n"
            case "\r": out += "\\r"
            case "\t": out += "\\t"
            default:
                if scalar.value < 0x20 {
                    out += String(format: "\\u%04x", scalar.value)
                } else {
                    out.unicodeScalars.append(scalar)
                }
            }
        }
        out += "\""
        return out
    }

    func installFileMenu() {
        guard let main = NSApp.mainMenu else { return }
        let fileItem = NSMenuItem()
        main.insertItem(fileItem, at: 1)
        let fileMenu = NSMenu(title: "File")
        fileItem.submenu = fileMenu
        fileMenu.addItem(NSMenuItem.separator())
        let openItem = NSMenuItem(
            title: "Open Folder…",
            action: #selector(openFolderPanel(_:)),
            keyEquivalent: "o"
        )
        openItem.target = self
        fileMenu.addItem(openItem)
    }

    @objc func openFolderPanel(_ sender: Any?) {
        NSApp.activate(ignoringOtherApps: true)
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.canCreateDirectories = true
        panel.prompt = "Open"
        panel.message = "Choose the project folder — this becomes your workspace for all LLM calls."
        if panel.runModal() == .OK, let url = panel.url {
            sendFolderToWeb(path: url.path)
        }
    }

    func sendFolderToWeb(path: String) {
        let literal = jsStringLiteral(path)
        let js = "void(window.forgeOpenFolder&&window.forgeOpenFolder(\(literal)));"
        DispatchQueue.main.async {
            self.webView.evaluateJavaScript(js, completionHandler: nil)
        }
        HeartLauncher.logLine("open folder \(path)")
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "forgeNative" else { return }
        if let body = message.body as? [String: Any], body["action"] as? String == "openFolder" {
            DispatchQueue.main.async { self.openFolderPanel(nil) }
        }
    }

    func installViewMenu() {
        guard let main = NSApp.mainMenu else { return }
        let viewItem = NSMenuItem()
        main.addItem(viewItem)
        let viewMenu = NSMenu(title: "View")
        viewItem.submenu = viewMenu
        viewMenu.addItem(
            withTitle: "Reload Forge IDE",
            action: #selector(reloadForgeUI),
            keyEquivalent: "r"
        )
    }

    @objc func reloadForgeUI() {
        let bust = Int(Date().timeIntervalSince1970)
        if let url = URL(string: "http://127.0.0.1:\(port)/terminal/index.html?ui=3.0.0&t=\(bust)") {
            var req = URLRequest(url: url)
            req.cachePolicy = .reloadIgnoringLocalCacheData
            webView.load(req)
            HeartLauncher.logLine("reload ui t=\(bust)")
        }
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        SinaStandaloneShell.installStandardMenu(appName: "Forge Terminal", includeEditing: true)
        installFileMenu()
        installViewMenu()
        HeartLauncher.logLine("double-click launch")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1440, height: 920),
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.title = "Forge Terminal"
        window.minSize = NSSize(width: 1024, height: 720)
        window.titlebarAppearsTransparent = true
        window.titleVisibility = .hidden
        window.isReleasedWhenClosed = false
        SinaStandaloneShell.showWindow(window)
        let config = WKWebViewConfiguration()
        let bridge = """
        window.forgeRequestNativeOpenFolder = function() {
          window.webkit.messageHandlers.forgeNative.postMessage({action:'openFolder'});
        };
        """
        config.userContentController.addUserScript(
            WKUserScript(source: bridge, injectionTime: .atDocumentStart, forMainFrameOnly: true)
        )
        let desktopFlag = """
        window.__FORGE_DESKTOP_APP__ = true;
        """
        config.userContentController.addUserScript(
            WKUserScript(source: desktopFlag, injectionTime: .atDocumentStart, forMainFrameOnly: true)
        )
        config.userContentController.add(self, name: "forgeNative")
        webView = ForgeWebView(frame: window.contentView!.bounds, configuration: config)
        webView.navigationDelegate = self
        webView.autoresizingMask = [.width, .height]
        window.contentView = webView
        window.makeFirstResponder(webView)
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
        <html><body style='background:#0b0f14;color:#e8eef7;font-family:system-ui;padding:48px;text-align:center'>
        <div style='font-size:2rem;margin-bottom:12px;color:#3dd68c'>⬡</div>
        <h1 style='font-weight:650;font-size:1.1rem'>Forge Terminal</h1>
        <p style='color:#73839a;font-size:0.9rem'>Starting local forge engine…</p>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func showFailure() {
        let html = """
        <html><body style='background:#0b0f14;color:#e8eef7;font-family:system-ui;padding:40px;text-align:center'>
        <h1 style='font-size:1.2rem'>Forge Terminal</h1>
        <p style='color:#73839a'>Server failed to start.</p>
        <button id='retry' style='margin-top:16px;padding:10px 18px;border:none;border-radius:8px;background:#3dd68c;color:#0b0f14;font-weight:650;cursor:pointer'>Retry</button>
        <p style='color:#73839a;font-size:0.85rem;margin-top:16px'>Log: ~/.sina/forge-terminal-app-launch.log</p>
        <script>
        document.getElementById('retry').onclick=function(){
          window.location.href='http://127.0.0.1:\(port)/?t='+Date.now();
        };
        </script>
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
        let alert = NSAlert()
        alert.messageText = "Forge Terminal"
        alert.informativeText = "Could not start the server. Use Retry in the window or check ~/.sina/forge-terminal-app-launch.log"
        alert.alertStyle = .warning
        alert.runModal()
    }

    func pollHealthAndLoad(attempts: Int) {
        guard let healthURL = URL(string: "http://127.0.0.1:\(port)/health") else { return }
        URLSession.shared.dataTask(with: healthURL) { _, resp, _ in
            DispatchQueue.main.async {
                if let http = resp as? HTTPURLResponse, http.statusCode == 200 {
                    let bust = Int(Date().timeIntervalSince1970)
                    let pageURL = URL(string: "http://127.0.0.1:\(self.port)/terminal/index.html?embed=1&desktop=1&ui=4.11.12-living-chat-fast&t=\(bust)")
                    let loadPage = {
                        guard let pageURL else { return }
                        HeartLauncher.logLine("window loading Forge IDE desktop (single page · scroll)")
                        var req = URLRequest(url: pageURL)
                        req.cachePolicy = .reloadIgnoringLocalCacheData
                        self.webView.load(req)
                    }
                    let store = WKWebsiteDataStore.default()
                    let types = WKWebsiteDataStore.allWebsiteDataTypes()
                    store.fetchDataRecords(ofTypes: types) { records in
                        let local = records.filter { $0.displayName.contains("127.0.0.1") || $0.displayName.contains("localhost") }
                        store.removeData(ofTypes: types, for: local) {
                            DispatchQueue.main.async { loadPage() }
                        }
                    }
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

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        webView.evaluateJavaScript(
            "document.getElementById('prompt-input') && document.getElementById('prompt-input').focus();",
            completionHandler: nil
        )
        window.makeFirstResponder(webView)
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
struct ForgeTerminalAppMain {
    static func main() {
        let bundleId = "com.sina.forgeterminal.standalone"
        if !SinaStandaloneShell.prepareApp(bundleId: bundleId) {
            return
        }
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}
