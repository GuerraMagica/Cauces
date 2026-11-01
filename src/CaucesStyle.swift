import SwiftUI
import AppKit

enum FlowTheme {
    static let background = Color(hex: 0x101619)
    static let surface = Color(hex: 0x182125)
    static let raised = Color(hex: 0x202B30)
    static let border = Color(hex: 0x334047)
    static let text = Color(hex: 0xF0F4F2)
    static let secondary = Color(hex: 0xA7B5B8)
    static let voice1 = Color(hex: 0x76D6C0)
    static let voice2 = Color(hex: 0xE2B883)
    static let residual = Color(hex: 0xA9B5BF)
    static let action = Color(hex: 0xA7E2D2)
    static let onAction = Color(hex: 0x102721)
    static let success = Color(hex: 0x9CE2C6)
}

private extension Color {
    init(hex: UInt32) {
        self.init(.sRGB, red: Double((hex >> 16) & 255)/255,
                  green: Double((hex >> 8) & 255)/255, blue: Double(hex & 255)/255, opacity: 1)
    }
}

struct FlowButtonStyle: ButtonStyle {
    var primary = false
    @Environment(\.isEnabled) private var enabled
    func makeBody(configuration: Configuration) -> some View {
        configuration.label.font(.system(size: 14, weight: .semibold))
            .padding(.horizontal, 20).frame(minHeight: 44)
            .foregroundStyle(primary ? FlowTheme.onAction : FlowTheme.text)
            .background(primary ? FlowTheme.action : FlowTheme.raised, in: RoundedRectangle(cornerRadius: 10))
            .overlay(RoundedRectangle(cornerRadius: 10).strokeBorder(primary ? FlowTheme.action : FlowTheme.border))
            .opacity(enabled ? (configuration.isPressed ? 0.75 : 1) : 0.45)
            .contentShape(RoundedRectangle(cornerRadius: 10))
    }
}

struct FlowArtwork: View {
    private static let image: NSImage? = {
        guard let url = Bundle.main.url(forResource: "FlowArtwork@2x", withExtension: "png"),
              let image = NSImage(contentsOf: url) else { return nil }
        image.size = NSSize(width: 500, height: 175)
        return image
    }()
    var body: some View {
        Group {
            if let image = Self.image {
                Image(nsImage: image).resizable().scaledToFit()
            }
        }.frame(maxWidth: 500, maxHeight: 175).accessibilityHidden(true)
    }
}

// Style only the window containing this view; file panels keep their native behavior.
struct FlowWindowStyle: NSViewRepresentable {
    final class WindowView: NSView {
        override func viewDidMoveToWindow() {
            super.viewDidMoveToWindow()
            window?.titlebarAppearsTransparent = true
            window?.backgroundColor = NSColor(srgbRed: 16/255, green: 22/255, blue: 25/255, alpha: 1)
            window?.appearance = NSAppearance(named: .darkAqua)
        }
    }
    func makeNSView(context: Context) -> WindowView { WindowView() }
    func updateNSView(_ nsView: WindowView, context: Context) {}
}
