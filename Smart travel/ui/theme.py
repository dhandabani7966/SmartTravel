import streamlit as st
import textwrap

def html_markdown(html_content: str):
    """Render HTML content safely by stripping leading/trailing whitespace of every line to prevent markdown code blocks parsing."""
    cleaned_lines = [line.strip() for line in html_content.splitlines()]
    cleaned_content = "\n".join(cleaned_lines)
    st.markdown(cleaned_content, unsafe_allow_html=True)


def get_theme_colors():
    """Return color tokens based on current dark/light mode preference."""
    is_dark = st.session_state.get("dark_mode", False)
    
    if is_dark:
        return {
            "primary": "#FF724C",       # Sunrise Coral
            "accent": "#FFC400",        # Warm Amber Gold
            "background": "#0D111A",    # Deep Space Indigo Midnight
            "sidebar_bg": "#141A29",
            "card_bg": "rgba(20, 26, 41, 0.8)",
            "text": "#F0F4F8",          # Ice Blue
            "text_muted": "#8E9DB2",
            "border": "#222A3C",
            "card_shadow": "0 12px 36px 0 rgba(0, 0, 0, 0.5)",
            "primary_glow": "rgba(255, 114, 76, 0.3)"
        }
    else:
        return {
            "primary": "#FF5E36",       # Sunset Coral
            "accent": "#FFB000",        # Amber Gold
            "background": "#FAF8F6",    # Creamy Sand White
            "sidebar_bg": "#F4EFEA",
            "card_bg": "rgba(255, 255, 255, 0.85)",
            "text": "#1E2538",          # Midnight Navy
            "text_muted": "#63728A",
            "border": "#ECE7E1",
            "card_shadow": "0 12px 30px 0 rgba(255, 94, 54, 0.08)",
            "primary_glow": "rgba(255, 94, 54, 0.2)"
        }

def inject_theme():
    """Inject Poppins & Inter fonts and global CSS styling into Streamlit."""
    colors = get_theme_colors()
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap');

    /* Variables and Globals */
    :root {{
        --primary: {colors["primary"]};
        --accent: {colors["accent"]};
        --bg: {colors["background"]};
        --card-bg: {colors["card_bg"]};
        --text: {colors["text"]};
        --text-muted: {colors["text_muted"]};
        --border: {colors["border"]};
        --primary-glow: {colors["primary_glow"]};
    }}

    /* Global Body Font Overrides */
    .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }}

    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {{
        font-family: 'Poppins', 'Sora', sans-serif !important;
        color: var(--text) !important;
    }}

    /* Remove default streamlit header margin and clean up look */
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Fix dark theme input widget labels & texts visibility */
    label, 
    [data-testid="stWidgetLabel"] p, 
    .stWidgetLabel, 
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stCaptionContainer"] p, 
    span[data-testid="stWidgetLabel"],
    [data-testid="stCheckbox"] p,
    [data-testid="stToggle"] p,
    .st-emotion-cache-1px78vs,
    .st-emotion-cache-1vt4y4q {{
        color: var(--text) !important;
        font-weight: 500 !important;
    }}

    /* Navigation Styling */
    .custom-nav {{
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 10px 20px;
        margin-bottom: 30px;
        box-shadow: {colors["card_shadow"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}
    
    .custom-nav-item {{
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        text-decoration: none;
        color: var(--text-muted);
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    }}

    .custom-nav-item:hover {{
        color: var(--primary);
        background: var(--primary-glow);
        transform: translateY(-1px);
    }}

    .custom-nav-item.active {{
        color: white !important;
        background: var(--primary) !important;
        box-shadow: 0 4px 12px var(--primary-glow);
    }}

    /* Cards */
    .glass-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        box-shadow: {colors["card_shadow"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 20px;
    }}

    .glass-card:hover {{
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.12);
        border-color: var(--primary);
    }}

    .glass-card p, .glass-card span, .glass-card li, .glass-card div {{
        color: var(--text) !important;
    }}

    /* Buttons */
    .stButton>button {{
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px var(--primary-glow) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }}

    .stButton>button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px var(--primary-glow) !important;
        opacity: 0.95;
    }}

    .stButton>button:active {{
        transform: translateY(-1px) !important;
    }}

    /* Input textboxes and selectboxes styling adjustments */
    div[data-baseweb="input"] {{
        background-color: var(--card-bg) !important;
        border-color: var(--border) !important;
    }}
    
    div[data-baseweb="select"] {{
        background-color: var(--card-bg) !important;
    }}

    /* Hide Sidebar Navigation elements */
    [data-testid="sidebar-nav-items"] {{
        display: none !important;
    }}
    
    /* Animation Keyframes Injections */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translate3d(0, 20px, 0);
        }}
        to {{
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }}
    }}

    .fade-in-up {{
        animation: fadeInUp 0.6s cubic-bezier(0.25, 1, 0.5, 1) both;
    }}

    @keyframes floatAnimation {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-6px); }}
        100% {{ transform: translateY(0px); }}
    }}

    .floating {{
        animation: floatAnimation 3.5s ease-in-out infinite;
    }}

    /* Shimmer Skeleton Placeholder */
    .shimmer {{
        background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.05) 75%);
        background-size: 200% 100%;
        animation: loadingShimmer 1.5s infinite;
        border-radius: 8px;
    }}

    @keyframes loadingShimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

