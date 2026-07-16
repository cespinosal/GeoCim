STEEL_900 = "#1b2330"
STEEL_800 = "#222c3c"

def get_stylesheet():
    return f"""
    QMainWindow {{
        background: #f4f6f9;
    }}
    QStatusBar {{
        background: {STEEL_900};
        color: #8b97a8;
        font-family: "IBM Plex Mono";
        font-size: 11px;
        border-top: 1px solid #11161f;
        padding: 2px 8px;
    }}
    QStatusBar::item {{
        border: none;
    }}
    """
