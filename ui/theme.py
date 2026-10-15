# TerTemiz / CCleaner Modern Color Palette and Design System
# Supports seamless Light and Dark modes using CustomTkinter's (light, dark) color tuples

class CCleanerTheme:
    # Brand Primary
    PRIMARY = "#ff6200"            # Vibrant Orange
    PRIMARY_HOVER = "#e65800"
    PRIMARY_LIGHT = "#ff8533"
    
    # Brand Secondary / Pro
    BLUE = "#0084ff"
    BLUE_HOVER = "#0070d9"
    GOLD = "#f59e0b"
    
    # State Colors
    SUCCESS = "#10b981"
    SUCCESS_HOVER = "#059669"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    DANGER_HOVER = "#dc2626"
    
    # Adaptive Dynamic Colors: (Light Mode, Dark Mode)
    BG_MAIN = ("#f4f6fa", "#121316")
    BG_SIDEBAR = ("#ffffff", "#181a1f")
    BG_CARD = ("#ffffff", "#21242b")
    BG_CARD_HOVER = ("#eef2f6", "#2a2d36")
    BG_INPUT = ("#edf2f7", "#1a1c22")
    BORDER = ("#cbd5e1", "#2e323d")
    
    # Adaptive Text Colors: (Light Mode, Dark Mode)
    TEXT_PRIMARY = ("#0f172a", "#ffffff")
    TEXT_SECONDARY = ("#334155", "#9ca3af")
    TEXT_MUTED = ("#64748b", "#6b7280")

    # Backward compatibility aliases pointing to adaptive tuples
    DARK_BG_MAIN = BG_MAIN
    DARK_BG_SIDEBAR = BG_SIDEBAR
    DARK_BG_CARD = BG_CARD
    DARK_BG_CARD_HOVER = BG_CARD_HOVER
    DARK_BG_INPUT = BG_INPUT
    DARK_BORDER = BORDER

    DARK_TEXT_PRIMARY = TEXT_PRIMARY
    DARK_TEXT_SECONDARY = TEXT_SECONDARY
    DARK_TEXT_MUTED = TEXT_MUTED

    LIGHT_BG_MAIN = BG_MAIN
    LIGHT_BG_SIDEBAR = BG_SIDEBAR
    LIGHT_BG_CARD = BG_CARD
    LIGHT_BG_CARD_HOVER = BG_CARD_HOVER
    LIGHT_BG_INPUT = BG_INPUT
    LIGHT_BORDER = BORDER

    LIGHT_TEXT_PRIMARY = TEXT_PRIMARY
    LIGHT_TEXT_SECONDARY = TEXT_SECONDARY
    LIGHT_TEXT_MUTED = TEXT_MUTED

    # Fonts
    FONT_FAMILY = "Segoe UI"
    
    @classmethod
    def get_font(cls, size=12, weight="normal"):
        return (cls.FONT_FAMILY, size, weight)
