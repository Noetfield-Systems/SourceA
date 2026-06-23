import Cocoa
import WebKit

enum SinaAppId: String {
    case hub
    case mail
    case chat
    case n8n
    case cloud
    case macLaw = "mac-law"
    case agRouting = "ag-routing"

    static func from(url: URL) -> SinaAppId? {
        if url.scheme == "sina-app", let host = url.host, let id = SinaAppId(rawValue: host) {
            return id
        }
        guard url.host == "127.0.0.1" || url.host == "localhost" else { return nil }
        let path = url.path
        if url.port == 13023 { return .chat }
        if url.port == 13026 { return .n8n }
        if url.port == 13027 { return .cloud }
        if url.port == 8782 { return .agRouting }
        if url.port == 8781 || path.contains("mac-law") { return .macLaw }
        if path.contains("/mail-hub") { return .mail }
        if path.contains("/cloud-workers") { return .cloud }
        if url.port == 13020 { return .hub }
        return nil
    }
}

final class SinaAppRouter: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
    let homeApp: SinaAppId
    weak var webView: WKWebView?

    init(homeApp: SinaAppId) {
        self.homeApp = homeApp
    }

    func prepare(config: WKWebViewConfiguration) {
        config.userContentController.add(self, name: "sinaAppOpen")
    }

    func attach(to webView: WKWebView) {
        self.webView = webView
        webView.navigationDelegate = self
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "sinaAppOpen" else { return }
        var appId: SinaAppId?
        if let body = message.body as? [String: Any], let raw = body["app"] as? String {
            appId = SinaAppId(rawValue: raw)
        } else if let raw = message.body as? String {
            appId = SinaAppId(rawValue: raw)
        }
        guard let appId = appId else { return }
        openApp(appId)
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationAction: WKNavigationAction,
        decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
    ) {
        guard navigationAction.navigationType == .linkActivated,
              let url = navigationAction.request.url,
              let target = SinaAppId.from(url: url) else {
            decisionHandler(.allow)
            return
        }
        if target == homeApp {
            decisionHandler(.allow)
            return
        }
        openApp(target)
        decisionHandler(.cancel)
    }

    func openApp(_ appId: SinaAppId) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        switch appId {
        case .mail:
            let app = home.appendingPathComponent("Desktop/Portfolio Mail.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:13020/mail-hub/")!)
        case .chat:
            let app = home.appendingPathComponent("Desktop/Chat Unify.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:13023/")!)
        case .n8n:
            let app = home.appendingPathComponent("Desktop/N8N Integration.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:13026/")!)
        case .hub:
            let app = home.appendingPathComponent("Desktop/Worker Hub.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:13020/")!)
        case .cloud:
            let app = home.appendingPathComponent("Desktop/Cloud Workers.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:13027/")!)
        case .macLaw:
            let app8781 = home.appendingPathComponent("Desktop/Mac Law.app")
            if FileManager.default.fileExists(atPath: app8781.path) {
                NSWorkspace.shared.open(app8781)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:8781/")!)
        case .agRouting:
            let app = home.appendingPathComponent("Desktop/AG Routing Panel.app")
            if FileManager.default.fileExists(atPath: app.path) {
                NSWorkspace.shared.open(app)
                return
            }
            NSWorkspace.shared.open(URL(string: "http://127.0.0.1:8782/")!)
        }
        NSApp.activate(ignoringOtherApps: false)
    }
}
