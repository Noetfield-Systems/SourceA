import Cocoa

enum SinaStandaloneShell {
    private static var retainedDelegate: NSApplicationDelegate?

    static func run(delegate: NSApplicationDelegate, bundleId: String) {
        retainedDelegate = delegate
        NSApp.setActivationPolicy(.regular)
        NSApp.delegate = delegate
        NSApp.run()
    }

    @discardableResult
    static func activateSingleInstance(bundleId: String) -> Bool {
        guard Bundle.main.bundleIdentifier == bundleId else { return true }
        _ = NSApplication.shared
        let me = ProcessInfo.processInfo.processIdentifier
        let others = NSRunningApplication.runningApplications(withBundleIdentifier: bundleId)
            .filter { $0.processIdentifier != me }
        guard let existing = others.first else { return true }
        existing.activate(options: [.activateAllWindows])
        return false
    }

    @discardableResult
    static func prepareApp(bundleId: String) -> Bool {
        _ = NSApplication.shared
        NSApp.setActivationPolicy(.regular)
        return activateSingleInstance(bundleId: bundleId)
    }

    static func showWindow(_ window: NSWindow) {
        window.center()
        window.makeKeyAndOrderFront(nil)
        window.orderFrontRegardless()
        NSApp.activate(ignoringOtherApps: true)
    }

    static func handleReopen(window: NSWindow?) -> Bool {
        if let window {
            showWindow(window)
        }
        return true
    }

    /// Standard app menu so ⌘Q Quit works in every standalone .app (required on macOS without storyboard menu).
    static func installStandardMenu(appName: String) {
        let main = NSMenu()
        let appMenuItem = NSMenuItem()
        main.addItem(appMenuItem)
        let appMenu = NSMenu(title: appName)
        appMenuItem.submenu = appMenu
        appMenu.addItem(
            withTitle: "About \(appName)",
            action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)),
            keyEquivalent: ""
        )
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(
            withTitle: "Quit \(appName)",
            action: #selector(NSApplication.terminate(_:)),
            keyEquivalent: "q"
        )
        NSApp.mainMenu = main
    }
}
